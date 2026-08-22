import pytest
from app.config import settings
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService
from app.services.segmenter import DocumentSegmenterService
from app.services.extractor import ClinicalEntityExtractorService

def test_entity_extractor():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)
    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)
    pages = DuplicateDetectorService.detect_duplicates(pages)
    docs = DocumentSegmenterService.segment_documents(pages)

    patient, encounters, conditions, symptoms, meds, allergies, procs, obs = ClinicalEntityExtractorService.extract_all(docs, pages)

    assert "Marcus" in patient.full_name and "Whitfield" in patient.full_name
    assert patient.dob == "1987-03-14"
    assert patient.mrn == "PCG-4471902"
    assert len(encounters) >= 15
    assert len(conditions) >= 5
    assert len(meds) >= 5
    assert len(procs) >= 5
    assert len(obs) >= 5

    # Verify provenance attached to entities
    assert all(len(c.provenance) > 0 for c in conditions)
    assert all(c.provenance[0].source_page >= 1 for c in conditions)
