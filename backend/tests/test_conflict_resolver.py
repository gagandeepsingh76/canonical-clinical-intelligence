import pytest
from app.config import settings
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService
from app.services.segmenter import DocumentSegmenterService
from app.services.extractor import ClinicalEntityExtractorService
from app.services.conflict_resolver import ConflictResolverService

def test_conflict_resolver():
    pdf_path = str(settings.BASE_DIR / "Synthetic_Medical_Record_Exercise_Whitfield 1.pdf")
    pages = PDFIngestionService.extract_pdf(pdf_path)
    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)
    pages = DuplicateDetectorService.detect_duplicates(pages)
    docs = DocumentSegmenterService.segment_documents(pages)

    patient, encounters, conditions, symptoms, meds, allergies, procs, obs = ClinicalEntityExtractorService.extract_all(docs, pages)

    conflicts, review_queue = ConflictResolverService.analyze_and_resolve(docs, pages, patient, conditions)

    assert len(conflicts) >= 2
    # Verify patient identity conflict
    id_conflicts = [c for c in conflicts if "patient" in c.field.lower()]
    assert len(id_conflicts) == 1
    assert 16 in id_conflicts[0].source_pages
    assert any("Whitmore" in val for val in id_conflicts[0].candidate_values)

    # Verify laterality conflict
    lat_conflicts = [c for c in conflicts if "laterality" in c.field.lower()]
    assert len(lat_conflicts) == 1
    assert 14 in lat_conflicts[0].source_pages

    # Verify review queue populated
    assert len(review_queue) >= 2
