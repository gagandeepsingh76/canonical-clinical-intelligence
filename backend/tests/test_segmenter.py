import pytest
from app.config import settings
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService
from app.services.segmenter import DocumentSegmenterService

def test_document_segmenter():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)
    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)
    pages = DuplicateDetectorService.detect_duplicates(pages)

    docs = DocumentSegmenterService.segment_documents(pages)
    assert len(docs) >= 15
    
    # Check start and end pages are valid
    for doc in docs:
        assert doc.start_page <= doc.end_page
        assert doc.document_type != "UNKNOWN"
