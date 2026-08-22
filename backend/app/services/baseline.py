import re
from typing import Dict, Any, List
from app.models.schemas import PageData

class NaiveBaselinePipeline:
    """
    Naive baseline pipeline for benchmarking:
    - Treats PDF as one continuous document
    - Basic regex extraction
    - No page classification (all UNKNOWN)
    - No document segmentation (1 single document)
    - No terminology normalization (no ICD-10/RxNorm/LOINC/CPT)
    - No deduplication (every mention creates a duplicate entity)
    - No conflict resolution
    """
    @classmethod
    def run(cls, pages: List[PageData]) -> Dict[str, Any]:
        # Concatenate entire document text
        full_text = "\n".join(p.cleaned_text for p in pages)
        
        # 1. Monolithic document
        documents_detected = 1
        
        # 2. Naive regex entity extraction (no deduplication, no normalization)
        # Conditions
        cond_matches = re.findall(r"(?:diagnosis|impression|assessment|condition)\s*[:\s]*([^\.\n]+)", full_text, re.IGNORECASE)
        conditions_found = [c.strip() for c in cond_matches]
        
        # Meds
        med_matches = re.findall(r"\b(cyclobenzaprine|flexeril|naproxen|tylenol|toradol|gabapentin|oxycodone|percocet|dexamethasone|bupivacaine|methocarbamol)\b", full_text, re.IGNORECASE)
        meds_found = [m.strip() for m in med_matches]
        
        # Patient
        pat_matches = re.findall(r"(?:Patient Name|Patient|Employee)\s*[:\s]*([A-Z][a-z]+,\s*[A-Z][a-z]+)", full_text)
        patient_found = pat_matches[0] if pat_matches else "Unknown"

        return {
            "pipeline_type": "Naive Baseline",
            "page_classification_implemented": False,
            "document_segmentation_implemented": False,
            "documents_detected": documents_detected,
            "terminology_normalization_implemented": False,
            "deduplication_implemented": False,
            "conflict_resolution_implemented": False,
            "fhir_r4_generation_implemented": False,
            "provenance_tracking_implemented": False,
            "total_extracted_conditions": len(conditions_found),
            "total_extracted_medications": len(meds_found),
            "conditions": conditions_found[:10],
            "medications": meds_found[:10],
            "patient": patient_found
        }
