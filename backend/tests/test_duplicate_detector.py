import pytest
from app.config import settings
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService

def test_duplicate_detector():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)
    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)

    pages = DuplicateDetectorService.detect_duplicates(pages)

    # Page 12 is a duplicate / unsigned draft of Page 10
    page_12 = [p for p in pages if p.page_number == 12][0]
    assert page_12.is_duplicate is True
    assert page_12.duplicate_of == 10
    
    # Page 1 is not a duplicate
    page_1 = [p for p in pages if p.page_number == 1][0]
    assert page_1.is_duplicate is False
