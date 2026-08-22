import pytest
import hashlib
from app.models.schemas import PageData, PageLayoutFeatures
from app.services.page_classifier import PageClassifierService
from app.services.duplicate_detector import DuplicateDetectorService
from app.services.segmenter import DocumentSegmenterService
from app.services.extractor import ClinicalEntityExtractorService
from app.services.conflict_resolver import ConflictResolverService
from app.services.fhir_builder import FHIRBuilderService

def create_synthetic_page(page_num: int, title: str, facility: str, patient_name: str, dob: str, date: str, body: str) -> PageData:
    raw = f"{facility}\n{title}\nPatient Name: {patient_name}\nDOB: {dob}\nDate of Service: {date}\n\n{body}"
    clean = "\n".join(l.strip() for l in raw.strip().split("\n") if l.strip())
    p_hash = hashlib.sha256(clean.lower().replace(" ", "").encode("utf-8")).hexdigest()
    return PageData(
        page_number=page_num,
        raw_text=raw,
        cleaned_text=clean,
        header=f"{facility} | {title}",
        footer="Signed",
        layout_features=PageLayoutFeatures(width=612, height=792, num_lines=10),
        text_density=0.001,
        page_hash=p_hash,
        is_blank=False
    )

def test_generalization_on_arbitrary_record():
    # Construct a synthetic record with 6 pages, novel patient 'Sarah Jenkins', novel clinic, novel dates
    p1 = create_synthetic_page(1, "AMBULANCE RUN REPORT", "CITY METRO EMS", "Jenkins, Sarah", "05/12/1992", "03/10/2023", "GCS 15. Pulse 78. Neck pain following fall. C-collar placed.")
    p2 = create_synthetic_page(2, "EMERGENCY PHYSICIAN NOTE", "ST. JUDE MEMORIAL HOSPITAL", "Jenkins, Sarah", "05/12/1992", "03/10/2023", "Diagnosis: Cervical strain. Prescribed Naproxen 500 mg.")
    p3 = create_synthetic_page(3, "MRI LUMBAR SPINE WITHOUT CONTRAST", "METRO IMAGING CENTER", "Jenkins, Sarah", "05/12/1992", "04/05/2023", "Impression: L4-L5 disc protrusion causing right L5 radiculopathy.")
    # Page 4 is a duplicate copy of Page 2 (different page number)
    p4 = create_synthetic_page(4, "EMERGENCY PHYSICIAN NOTE", "ST. JUDE MEMORIAL HOSPITAL", "Jenkins, Sarah", "05/12/1992", "03/10/2023", "Diagnosis: Cervical strain. Prescribed Naproxen 500 mg.")
    # Page 5 is an operative note
    p5 = create_synthetic_page(5, "OPERATIVE REPORT", "ST. JUDE SURGERY CENTER", "Jenkins, Sarah", "05/12/1992", "06/15/2023", "Procedure: Right L4-L5 Lumbar Microdiscectomy. Performed by Dr. Miller.")
    # Page 6 is a conflicting patient chart accidentally included (Emma Jenkins, DOB 11/04/1980)
    p6 = create_synthetic_page(6, "OFFICE VISIT NOTE - PRIMARY CARE", "VALLEY HEALTH CLINIC", "Jenkins, Emma", "11/04/1980", "07/01/2023", "Routine wellness checkup.")

    pages = [p1, p2, p3, p4, p5, p6]

    # 1. Classification
    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)

    assert p1.predicted_document_type == "EMS_REPORT"
    assert p2.predicted_document_type == "PHYSICIAN_NOTE"
    assert p3.predicted_document_type == "RADIOLOGY_REPORT"
    assert p4.predicted_document_type == "PHYSICIAN_NOTE"
    assert p5.predicted_document_type == "OPERATIVE_REPORT"
    assert p6.predicted_document_type == "PRIMARY_CARE_NOTE"

    # 2. Duplicate Detection
    pages = DuplicateDetectorService.detect_duplicates(pages)
    assert pages[3].is_duplicate is True
    assert pages[3].duplicate_of == 2
    assert pages[0].is_duplicate is False

    # 3. Document Segmentation
    docs = DocumentSegmenterService.segment_documents(pages)
    assert len(docs) >= 5

    # 4. Entity Extraction
    patient, encounters, conditions, symptoms, meds, allergies, procs, obs = ClinicalEntityExtractorService.extract_all(docs, pages)

    assert patient.full_name == "Sarah Jenkins"
    assert patient.dob == "1992-05-12"
    assert len(encounters) >= 4
    assert any(c.name == "Cervical strain" for c in conditions)
    assert any(m.name == "Naproxen" for m in meds)
    assert any(pr.name == "Right L4-L5 Lumbar Microdiscectomy" for pr in procs)

    # 5. Conflict Resolution
    conflicts, review_queue = ConflictResolverService.analyze_and_resolve(docs, pages, patient, conditions)

    # Must catch the identity conflict between Sarah Jenkins and Emma Jenkins
    assert len(conflicts) >= 1
    assert any("Sarah" in c.candidate_values[0] and "Emma" in c.candidate_values[1] for c in conflicts)
    assert any(q.entity_type == "Patient" for q in review_queue)

    # 6. FHIR R4 Bundle Validation
    bundle, val_report = FHIRBuilderService.build_and_validate_bundle(
        patient, encounters, conditions, meds, allergies, procs, obs, docs
    )
    assert bundle["resourceType"] == "Bundle"
    assert val_report["pass_rate_percentage"] == 100.0
    assert val_report["status"] == "PASSED"

def test_multipage_document_continuation_and_reordering():
    # Multi-page operative note where page 1 and page 2 share title, facility, date, patient
    p1 = create_synthetic_page(1, "OPERATIVE REPORT", "OAK VALLEY SURGICAL HOSPITAL", "Thorne, Robert", "08/21/1975", "10/05/2023", "Part 1: Pre-op diagnosis: Lumbar disc herniation. Incision made.")
    p2 = create_synthetic_page(2, "OPERATIVE REPORT", "OAK VALLEY SURGICAL HOSPITAL", "Thorne, Robert", "08/21/1975", "10/05/2023", "Part 2: Decompression completed. Hemostasis achieved. Wound closed.")
    # Page 3 is a discharge summary from the same hospital on next day
    p3 = create_synthetic_page(3, "DISCHARGE SUMMARY", "OAK VALLEY SURGICAL HOSPITAL", "Thorne, Robert", "08/21/1975", "10/06/2023", "Discharged home in stable condition. Prescribed Gabapentin 300 mg.")

    pages = [p1, p2, p3]

    for p in pages:
        p.predicted_document_type, p.classification_confidence, _ = PageClassifierService.classify_page(p)

    pages = DuplicateDetectorService.detect_duplicates(pages)
    docs = DocumentSegmenterService.segment_documents(pages)

    # Pages 1 & 2 should be merged into a single multi-page LogicalDocument!
    assert len(docs) == 2
    assert docs[0].start_page == 1
    assert docs[0].end_page == 2
    assert docs[0].page_count == 2
    assert docs[1].start_page == 3

    patient, encounters, conditions, symptoms, meds, allergies, procs, obs = ClinicalEntityExtractorService.extract_all(docs, pages)
    assert patient.full_name == "Robert Thorne"
    assert patient.dob == "1975-08-21"
    assert any(m.name == "Gabapentin" for m in meds)
