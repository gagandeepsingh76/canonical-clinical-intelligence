import pytest
from app.config import settings
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService

def test_page_classifier():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)

    expected = {
        1: "EMS_REPORT",
        2: "EMERGENCY_DEPARTMENT_RECORD",
        3: "PHYSICIAN_NOTE",
        4: "RADIOLOGY_REPORT",
        5: "DISCHARGE_SUMMARY",
        6: "PRIMARY_CARE_NOTE",
        7: "PHYSICAL_THERAPY_EVALUATION",
        8: "RADIOLOGY_REPORT",
        9: "ORTHOPEDIC_SPINE_CONSULTATION",
        10: "PHYSICAL_THERAPY_PROGRESS_NOTE",
        11: "OPERATIVE_REPORT",
        12: "PHYSICAL_THERAPY_PROGRESS_NOTE",
        13: "ORTHOPEDIC_SPINE_CONSULTATION",
        14: "RADIOLOGY_REPORT",
        15: "OPERATIVE_REPORT",
        16: "DISCHARGE_SUMMARY",
        17: "PHYSICIAN_NOTE",
        18: "HISTORICAL_MEDICAL_RECORD",
        19: "MEDICATION_RECORD",
        20: "BILLING_RECORD",
        21: "EMPLOYER_WORK_STATUS",
        22: "RECORDS_CERTIFICATION",
    }

    for p in pages:
        doc_type, conf, sigs = PageClassifierService.classify_page(p)
        assert doc_type == expected[p.page_number], f"Page {p.page_number} expected {expected[p.page_number]}, got {doc_type}"
        assert conf >= 0.80
