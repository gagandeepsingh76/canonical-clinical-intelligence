import pytest
from pathlib import Path
from app.config import settings
from app.services.pipeline import MedicalRecordPipeline
from app.db.session import init_db, SessionLocal
from app.db.repository import Repository

def test_30plus_page_dataset_pipeline_end_to_end():
    pdf_path = settings.DATA_DIR / "synthetic_30plus_compliance_record.pdf"
    
    # Ensure PDF exists or generate
    if not pdf_path.exists():
        from data.generate_compliance_pdf import generate_30plus_compliance_pdf
        generate_30plus_compliance_pdf(str(pdf_path))
        
    assert pdf_path.exists()
    
    init_db()
    db = SessionLocal()
    try:
        # Process through exact same pipeline without shortcuts
        result = MedicalRecordPipeline.process_pdf(str(pdf_path), db=db)
        
        # 1. Ingestion & Page Count Requirement: >= 30 pages
        assert len(result.pages) >= 30
        assert len(result.pages) == 32
        
        # 2. Document Classification & Segmentation
        assert len(result.documents) >= 25
        doc_types = set(d.document_type for d in result.documents)
        assert len(doc_types) >= 8
        
        # 3. Duplicate Detection & Quarantine
        dup_pages = [p for p in result.pages if p.is_duplicate]
        assert len(dup_pages) >= 1
        assert any(p.page_number == 15 for p in dup_pages)
        
        # 4. Clinical Entity Extraction
        assert "Eleanor" in result.patient.full_name and "Vance" in result.patient.full_name
        assert result.patient.dob == "1985-06-18"
        assert result.patient.mrn == "MWH-882910"
        assert len(result.encounters) >= 15
        assert len(result.conditions) >= 5
        assert len(result.medications) >= 5
        assert len(result.procedures) >= 5
        assert len(result.observations) >= 5
        
        # 5. Conflict Resolution & Review Queue
        assert len(result.conflicts) >= 1
        assert any("Vance, Arthur" in val for c in result.conflicts for val in c.candidate_values)
        assert len(result.review_queue) >= 1
        
        # 6. FHIR R4 Bundle Validation
        assert result.fhir_validation["status"] == "PASSED"
        assert result.fhir_validation["pass_rate_percentage"] == 100.0
        assert result.fhir_validation["total_resources"] >= 100
        
        # 7. Database Persistence
        repo = Repository(db)
        db_patient = repo.get_patient()
        assert db_patient is not None
        assert "Eleanor" in db_patient.full_name
        assert len(repo.get_documents()) >= 25
    finally:
        db.close()
