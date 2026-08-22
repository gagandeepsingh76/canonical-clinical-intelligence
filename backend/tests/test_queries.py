import pytest
from app.config import settings
from app.db.session import init_db, SessionLocal
from app.services.pipeline import MedicalRecordPipeline
from app.services.query_engine import ClinicalQueryEngine

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    MedicalRecordPipeline.process_pdf(pdf_path, db=db)
    yield db
    db.close()

def test_all_clinical_queries(db_session):
    engine = ClinicalQueryEngine(db_session)

    # 1. Timeline
    timeline = engine.query_patient_timeline()
    assert len(timeline) >= 15
    assert any("02/11/2024" in ev["date"] for ev in timeline)

    # 2. Diagnoses
    diagnoses = engine.query_diagnoses_with_provenance()
    assert len(diagnoses) >= 5
    assert any(d["diagnosis_name"] == "Right lumbar radiculopathy" for d in diagnoses)
    assert all(len(d["source_pages"]) > 0 for d in diagnoses)

    # 3. Medications
    meds = engine.query_medication_history()
    assert len(meds) >= 5
    assert any(m["name"] in ["Methocarbamol", "Naproxen", "Gabapentin"] for m in meds)

    # 4. Abnormal observations
    obs = engine.query_abnormal_observations()
    assert len(obs) >= 5

    # 5. Lumbar radiculopathy
    rad_records = engine.query_lumbar_radiculopathy_records()
    assert len(rad_records["conditions"]) > 0
    assert len(rad_records["procedures"]) > 0

    # 6. Conflicts
    conflicts = engine.query_conflicts_requiring_review()
    assert len(conflicts) >= 2

    # 7. Page info
    page15_info = engine.query_page_extracted_info(15)
    assert page15_info["predicted_document_type"] == "OPERATIVE_REPORT"

    # 8. Procedures
    procs = engine.query_procedure_history()
    assert len(procs) >= 5

    # 9. Pain progression
    pain = engine.query_pain_progression()
    assert len(pain) >= 1
