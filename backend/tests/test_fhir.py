import pytest
from app.config import settings
from app.services.pipeline import MedicalRecordPipeline

def test_fhir_bundle_generation_and_validation():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    result = MedicalRecordPipeline.process_pdf(pdf_path)

    assert result.fhir_bundle is not None
    assert result.fhir_bundle["resourceType"] == "Bundle"
    assert len(result.fhir_bundle["entry"]) > 20
    
    # Check validation report
    val = result.fhir_validation
    assert val["status"] == "PASSED"
    assert val["pass_rate_percentage"] == 100.0
    assert len(val["errors"]) == 0
