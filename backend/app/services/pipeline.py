import time
from typing import Optional
from sqlalchemy.orm import Session
from app.models.schemas import PipelineResult
from app.services.ingestion import PDFIngestionService
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService
from app.services.segmenter import DocumentSegmenterService
from app.services.extractor import ClinicalEntityExtractorService
from app.services.normalizer import TerminologyNormalizerService
from app.services.deduplicator import DeduplicationService
from app.services.conflict_resolver import ConflictResolverService
from app.services.fhir_builder import FHIRBuilderService
from app.db.repository import Repository

class MedicalRecordPipeline:
    @classmethod
    def process_pdf(cls, pdf_path: str, db: Optional[Session] = None) -> PipelineResult:
        start_time = time.time()
        
        # 1. Ingestion
        pages = PDFIngestionService.extract_pdf(pdf_path)
        
        # 2. Classification
        for p in pages:
            doc_type, conf, sigs = PageClassifierService.classify_page(p)
            p.predicted_document_type = doc_type
            p.classification_confidence = conf
            p.classification_signals = sigs

        # 3. Duplicate Detection
        pages = DuplicateDetectorService.detect_duplicates(pages)

        # 4. Document Boundary Detection & Logical Document Grouping
        documents = DocumentSegmenterService.segment_documents(pages)

        # 5. Entity Extraction
        (
            patient, encounters, conditions,
            symptoms, medications, allergies,
            procedures, observations
        ) = ClinicalEntityExtractorService.extract_all(documents, pages)

        # 6. Terminology Normalization
        normalizer = TerminologyNormalizerService()
        normalizer.normalize_all(conditions, medications, observations, procedures)

        # 7. Deduplication & Entity Resolution
        conditions = DeduplicationService.deduplicate_conditions(conditions)
        medications = DeduplicationService.deduplicate_medications(medications)
        procedures = DeduplicationService.deduplicate_procedures(procedures)

        # 8. Conflict Detection & Resolution Policy
        conflicts, review_queue = ConflictResolverService.analyze_and_resolve(
            documents, pages, patient, conditions
        )

        # 9. FHIR R4 Bundle Generation & Validation
        fhir_bundle, fhir_validation = FHIRBuilderService.build_and_validate_bundle(
            patient, encounters, conditions, medications,
            allergies, procedures, observations, documents
        )

        elapsed_ms = round((time.time() - start_time) * 1000, 2)

        result = PipelineResult(
            success=True,
            filename=pdf_path.split("\\")[-1].split("/")[-1],
            total_pages=len(pages),
            pages=pages,
            documents=documents,
            patient=patient,
            encounters=encounters,
            conditions=conditions,
            symptoms=symptoms,
            medications=medications,
            allergies=allergies,
            procedures=procedures,
            observations=observations,
            conflicts=conflicts,
            review_queue=review_queue,
            fhir_bundle=fhir_bundle,
            fhir_validation=fhir_validation,
            execution_time_ms=elapsed_ms
        )

        # 10. Database Persistence
        if db:
            repo = Repository(db)
            repo.save_pipeline_result(result)

        return result
