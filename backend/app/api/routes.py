import os
import shutil
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.db.session import get_db
from app.db.repository import Repository
from app.models.schemas import PipelineResult
from app.services.pipeline import MedicalRecordPipeline
from app.services.query_engine import ClinicalQueryEngine
from app.services.evaluator import PipelineEvaluatorService
from app.services.normalizer_evaluator import TerminologyEvaluatorService
import threading

router = APIRouter()

# Global memory cache for the latest processed pipeline result
_LATEST_RESULT: Optional[PipelineResult] = None
_PIPELINE_LOCK = threading.Lock()

class QueryRequest(BaseModel):
    query_name: str
    param: Optional[str] = None

@router.post("/process", response_model=PipelineResult)
def process_default_record(db: Session = Depends(get_db)):
    global _LATEST_RESULT
    default_file = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    if not Path(default_file).exists():
        raise HTTPException(status_code=404, detail="Default PDF file not found")
    
    result = MedicalRecordPipeline.process_pdf(default_file, db=db)
    _LATEST_RESULT = result
    return result

@router.post("/process-compliance", response_model=PipelineResult)
def process_compliance_record(db: Session = Depends(get_db)):
    global _LATEST_RESULT
    comp_file = settings.DATA_DIR / "synthetic_30plus_compliance_record.pdf"
    if not comp_file.exists():
        from data.generate_compliance_pdf import generate_30plus_compliance_pdf
        generate_30plus_compliance_pdf(str(comp_file))
    
    with _PIPELINE_LOCK:
        result = MedicalRecordPipeline.process_pdf(str(comp_file), db=db)
        _LATEST_RESULT = result
        return result

@router.post("/upload")
def upload_and_process_record(file: UploadFile = File(...), db: Session = Depends(get_db)):
    global _LATEST_RESULT
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    save_path = settings.DATA_DIR / file.filename
    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    with _PIPELINE_LOCK:
        result = MedicalRecordPipeline.process_pdf(str(save_path), db=db)
        _LATEST_RESULT = result
        return result

@router.get("/patient")
def get_patient(db: Session = Depends(get_db)):
    repo = Repository(db)
    patient = repo.get_patient()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found. Run pipeline first.")
    return patient

@router.get("/documents")
def get_documents(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_documents()

@router.get("/documents/{doc_id}/pages")
def get_document_pages(doc_id: str, db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_document_pages(doc_id=doc_id)

@router.get("/encounters")
def get_encounters(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_encounters()

@router.get("/conditions")
def get_conditions(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_conditions()

@router.get("/medications")
def get_medications(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_medications()

@router.get("/allergies")
def get_allergies(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_allergies()

@router.get("/procedures")
def get_procedures(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_procedures()

@router.get("/observations")
def get_observations(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_observations()

@router.get("/conflicts")
def get_conflicts(db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_conflicts()

@router.get("/review-queue")
def get_review_queue(status: Optional[str] = None, db: Session = Depends(get_db)):
    repo = Repository(db)
    return repo.get_review_queue(status=status)

@router.post("/review-queue/{queue_id}/update")
def update_review_queue_item(
    queue_id: str,
    status: str = Form(...),
    corrected_value: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    repo = Repository(db)
    updated = repo.update_review_item(queue_id, status, corrected_value, notes)
    if not updated:
        raise HTTPException(status_code=404, detail="Review item not found")
    return {"success": True, "item": updated}

@router.get("/fhir/bundle")
def get_fhir_bundle():
    bundle_file = settings.OUTPUT_DIR / "fhir_bundle.json"
    if not bundle_file.exists():
        raise HTTPException(status_code=404, detail="FHIR bundle not generated yet. Run pipeline first.")
    with open(bundle_file, "r", encoding="utf-8") as f:
        import json
        return json.load(f)

@router.get("/fhir/validation")
def get_fhir_validation():
    val_file = settings.OUTPUT_DIR / "fhir_validation_report.json"
    if not val_file.exists():
        raise HTTPException(status_code=404, detail="FHIR validation report not generated yet.")
    with open(val_file, "r", encoding="utf-8") as f:
        import json
        return json.load(f)

@router.get("/evaluation")
def get_evaluation(db: Session = Depends(get_db)):
    global _LATEST_RESULT
    if _LATEST_RESULT is None:
        default_file = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
        _LATEST_RESULT = MedicalRecordPipeline.process_pdf(default_file, db=db)
    
    return PipelineEvaluatorService.evaluate(_LATEST_RESULT)

@router.get("/evaluation/terminology")
def get_terminology_evaluation():
    return TerminologyEvaluatorService.evaluate_benchmark()

@router.post("/queries/run")
def run_clinical_query(
    req: QueryRequest,
    db: Session = Depends(get_db)
):
    engine = ClinicalQueryEngine(db)
    query_name = req.query_name
    param = req.param
    
    if query_name == "timeline":
        return {"query": "Patient Timeline", "results": engine.query_patient_timeline()}
    elif query_name == "diagnoses":
        return {"query": "Diagnoses with Provenance", "results": engine.query_diagnoses_with_provenance()}
    elif query_name == "medications":
        return {"query": "Medication History", "results": engine.query_medication_history()}
    elif query_name == "abnormal_observations":
        return {"query": "Abnormal Observations", "results": engine.query_abnormal_observations()}
    elif query_name == "lumbar_radiculopathy":
        return {"query": "Lumbar Radiculopathy & L4-L5 Records", "results": engine.query_lumbar_radiculopathy_records()}
    elif query_name == "conflicts":
        return {"query": "Conflicts Requiring Review", "results": engine.query_conflicts_requiring_review()}
    elif query_name == "page_info":
        page_num = int(param) if param and param.isdigit() else 1
        return {"query": f"Page {page_num} Extracted Info", "results": engine.query_page_extracted_info(page_num)}
    elif query_name == "procedures":
        return {"query": "Procedure History", "results": engine.query_procedure_history()}
    elif query_name == "pain_progression":
        return {"query": "Pain Score Progression", "results": engine.query_pain_progression()}
    else:
        raise HTTPException(status_code=400, detail=f"Unknown query: {query_name}")
