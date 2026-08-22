import pytest
from pathlib import Path
from app.config import settings
from app.services.ingestion import PDFIngestionService

def test_pdf_ingestion():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)
    
    assert len(pages) == 22
    assert pages[0].page_number == 1
    assert len(pages[0].cleaned_text) > 100
    assert pages[0].page_hash is not None
    assert pages[0].layout_features.width > 0
    assert pages[0].layout_features.height > 0
    assert not pages[0].is_blank
