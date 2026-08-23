from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.db_models import (
    DBPatient, DBDocument, DBDocumentPage, DBEncounter,
    DBCondition, DBMedication, DBAllergy, DBProcedure,
    DBObservation, DBConflict, DBReviewQueue
)
from app.models.schemas import PipelineResult

class Repository:
    def __init__(self, db: Session):
        self.db = db

    def save_pipeline_result(self, result: PipelineResult):
        try:
            # 1. Clear existing data in reverse dependency order
            self.db.query(DBReviewQueue).delete()
            self.db.query(DBConflict).delete()
            self.db.query(DBObservation).delete()
            self.db.query(DBProcedure).delete()
            self.db.query(DBAllergy).delete()
            self.db.query(DBMedication).delete()
            self.db.query(DBCondition).delete()
            self.db.query(DBEncounter).delete()
            self.db.query(DBDocumentPage).delete()
            self.db.query(DBDocument).delete()
            self.db.query(DBPatient).delete()
            self.db.flush()

            # 2. Resolve and save canonical Patient record first
            p = result.patient
            resolved_patient_id = p.patient_id if p and p.patient_id else "pat_001"
            db_patient = DBPatient(
                patient_id=resolved_patient_id,
                full_name=p.full_name if p and p.full_name else "Unknown Patient",
                first_name=p.first_name if p else None,
                last_name=p.last_name if p else None,
                dob=p.dob if p else None,
                gender=p.gender if p else None,
                mrn=p.mrn if p else None,
                phone=p.phone if p else None,
                address=p.address if p else None,
                employer=p.employer if p else None,
                is_canonical=p.is_canonical if p else True,
                confidence=p.confidence if p else 1.0
            )
            self.db.add(db_patient)
            self.db.flush()  # Ensures patient row exists before any dependent table is populated

            # 3. Save Documents & Pages
            saved_doc_ids = set()
            for doc in result.documents:
                saved_doc_ids.add(doc.document_id)
                db_doc = DBDocument(
                    document_id=doc.document_id,
                    document_type=doc.document_type,
                    title=doc.title,
                    facility_name=doc.facility_name,
                    provider_name=doc.provider_name,
                    service_date=doc.service_date,
                    start_page=doc.start_page,
                    end_page=doc.end_page,
                    page_count=doc.page_count,
                    classification_confidence=doc.classification_confidence,
                    is_historical=doc.is_historical,
                    is_conflicting_patient=doc.is_conflicting_patient,
                    raw_text=doc.raw_text
                )
                self.db.add(db_doc)
            self.db.flush()

            for page in result.pages:
                doc_id = None
                for doc in result.documents:
                    if doc.start_page <= page.page_number <= doc.end_page:
                        doc_id = doc.document_id
                        break
                
                db_page = DBDocumentPage(
                    document_id=doc_id if doc_id in saved_doc_ids else None,
                    page_number=page.page_number,
                    raw_text=page.raw_text,
                    cleaned_text=page.cleaned_text,
                    header=page.header,
                    footer=page.footer,
                    page_hash=page.page_hash,
                    is_blank=page.is_blank,
                    is_duplicate=page.is_duplicate,
                    duplicate_of=page.duplicate_of,
                    predicted_document_type=page.predicted_document_type,
                    classification_confidence=page.classification_confidence,
                    layout_features=page.layout_features.dict() if hasattr(page.layout_features, 'dict') else (page.layout_features.model_dump() if hasattr(page.layout_features, 'model_dump') else page.layout_features)
                )
                self.db.add(db_page)
            self.db.flush()

            # 4. Save Encounters
            saved_encounter_ids = set()
            for enc in result.encounters:
                saved_encounter_ids.add(enc.encounter_id)
                db_enc = DBEncounter(
                    encounter_id=enc.encounter_id,
                    patient_id=resolved_patient_id,
                    encounter_date=enc.encounter_date,
                    encounter_type=enc.encounter_type,
                    facility=enc.facility,
                    provider=enc.provider,
                    department=enc.department,
                    chief_complaint=enc.chief_complaint,
                    disposition=enc.disposition,
                    is_historical=enc.is_historical,
                    confidence=enc.confidence
                )
                self.db.add(db_enc)
            self.db.flush()

            # 5. Helper for provenance serialization
            def serialize_prov(prov_list):
                if not prov_list:
                    return None
                out = []
                for pr in prov_list:
                    if hasattr(pr, 'dict'):
                        out.append(pr.dict())
                    elif hasattr(pr, 'model_dump'):
                        out.append(pr.model_dump())
                    elif isinstance(pr, dict):
                        out.append(pr)
                return out

            # 6. Save Conditions
            for cond in result.conditions:
                enc_id = cond.encounter_id if cond.encounter_id in saved_encounter_ids else None
                db_cond = DBCondition(
                    condition_id=cond.condition_id,
                    patient_id=resolved_patient_id,
                    encounter_id=enc_id,
                    name=cond.name,
                    clinical_status=cond.clinical_status,
                    verification_status=cond.verification_status,
                    onset_date=cond.onset_date,
                    recorded_date=cond.recorded_date,
                    body_site=cond.body_site,
                    is_historical=cond.is_historical,
                    icd10_code=cond.terminology.code if cond.terminology else None,
                    icd10_display=cond.terminology.display if cond.terminology else None,
                    terminology_confidence=cond.terminology.mapping_confidence if cond.terminology else 0.0,
                    confidence=cond.confidence,
                    provenance=serialize_prov(cond.provenance)
                )
                self.db.add(db_cond)

            # 7. Save Medications
            for med in result.medications:
                enc_id = med.encounter_id if med.encounter_id in saved_encounter_ids else None
                db_med = DBMedication(
                    medication_id=med.medication_id,
                    patient_id=resolved_patient_id,
                    encounter_id=enc_id,
                    name=med.name,
                    dose=med.dose,
                    route=med.route,
                    frequency=med.frequency,
                    status=med.status,
                    prescribed_date=med.prescribed_date,
                    dispensed_date=med.dispensed_date,
                    indication=med.indication,
                    adverse_reactions=med.adverse_reactions,
                    rxnorm_code=med.terminology.code if med.terminology else None,
                    rxnorm_display=med.terminology.display if med.terminology else None,
                    terminology_confidence=med.terminology.mapping_confidence if med.terminology else 0.0,
                    confidence=med.confidence,
                    provenance=serialize_prov(med.provenance)
                )
                self.db.add(db_med)

            # 8. Save Allergies
            for alg in result.allergies:
                enc_id = alg.encounter_id if alg.encounter_id in saved_encounter_ids else None
                db_alg = DBAllergy(
                    allergy_id=alg.allergy_id,
                    patient_id=resolved_patient_id,
                    encounter_id=enc_id,
                    allergen=alg.allergen,
                    reaction=alg.reaction,
                    certainty=alg.certainty,
                    status=alg.status,
                    recorded_date=alg.recorded_date,
                    source=alg.source,
                    confidence=alg.confidence,
                    provenance=serialize_prov(alg.provenance)
                )
                self.db.add(db_alg)

            # 9. Save Procedures
            for proc in result.procedures:
                enc_id = proc.encounter_id if proc.encounter_id in saved_encounter_ids else None
                db_proc = DBProcedure(
                    procedure_id=proc.procedure_id,
                    patient_id=resolved_patient_id,
                    encounter_id=enc_id,
                    name=proc.name,
                    status=proc.status,
                    performed_date=proc.performed_date,
                    performer=proc.performer,
                    location=proc.location,
                    findings=proc.findings,
                    cpt_code=proc.terminology.code if proc.terminology else None,
                    cpt_display=proc.terminology.display if proc.terminology else None,
                    terminology_confidence=proc.terminology.mapping_confidence if proc.terminology else 0.0,
                    confidence=proc.confidence,
                    provenance=serialize_prov(proc.provenance)
                )
                self.db.add(db_proc)

            # 10. Save Observations
            for obs in result.observations:
                enc_id = obs.encounter_id if obs.encounter_id in saved_encounter_ids else None
                db_obs = DBObservation(
                    observation_id=obs.observation_id,
                    patient_id=resolved_patient_id,
                    encounter_id=enc_id,
                    category=obs.category,
                    name=obs.name,
                    value_string=obs.value_string,
                    value_numeric=obs.value_numeric,
                    unit=obs.unit,
                    reference_range=obs.reference_range,
                    interpretation=obs.interpretation,
                    effective_date=obs.effective_date,
                    loinc_code=obs.terminology.code if obs.terminology else None,
                    loinc_display=obs.terminology.display if obs.terminology else None,
                    terminology_confidence=obs.terminology.mapping_confidence if obs.terminology else 0.0,
                    confidence=obs.confidence,
                    provenance=serialize_prov(obs.provenance)
                )
                self.db.add(db_obs)
            self.db.flush()

            # 11. Save Conflicts
            for c in result.conflicts:
                db_c = DBConflict(
                    conflict_id=c.conflict_id,
                    field=c.field,
                    candidate_values=c.candidate_values,
                    source_documents=c.source_documents,
                    source_pages=c.source_pages,
                    confidence=c.confidence,
                    resolution=c.resolution,
                    resolution_reason=c.resolution_reason,
                    requires_review=c.requires_review,
                    status=c.status
                )
                self.db.add(db_c)

            # 12. Save Review Queue Items
            for q in result.review_queue:
                db_q = DBReviewQueue(
                    queue_id=q.queue_id,
                    entity_type=q.entity_type,
                    entity_id=q.entity_id,
                    field=q.field,
                    current_value=q.current_value,
                    confidence=q.confidence,
                    reason=q.reason,
                    source_page=q.source_page,
                    source_document_id=q.source_document_id if q.source_document_id in saved_doc_ids else (list(saved_doc_ids)[0] if saved_doc_ids else "doc_001"),
                    status=q.status,
                    corrected_value=q.corrected_value,
                    reviewer_notes=q.reviewer_notes
                )
                self.db.add(db_q)

            self.db.flush()
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e

    def get_patient(self) -> Optional[DBPatient]:
        return self.db.query(DBPatient).first()

    def get_documents(self) -> List[DBDocument]:
        return self.db.query(DBDocument).order_by(DBDocument.start_page).all()

    def get_document_pages(self, doc_id: Optional[str] = None) -> List[DBDocumentPage]:
        q = self.db.query(DBDocumentPage)
        if doc_id:
            q = q.filter(DBDocumentPage.document_id == doc_id)
        return q.order_by(DBDocumentPage.page_number).all()

    def get_encounters(self) -> List[DBEncounter]:
        return self.db.query(DBEncounter).order_by(DBEncounter.encounter_date).all()

    def get_conditions(self) -> List[DBCondition]:
        return self.db.query(DBCondition).all()

    def get_medications(self) -> List[DBMedication]:
        return self.db.query(DBMedication).all()

    def get_allergies(self) -> List[DBAllergy]:
        return self.db.query(DBAllergy).all()

    def get_procedures(self) -> List[DBProcedure]:
        return self.db.query(DBProcedure).order_by(DBProcedure.performed_date).all()

    def get_observations(self) -> List[DBObservation]:
        return self.db.query(DBObservation).order_by(DBObservation.effective_date).all()

    def get_conflicts(self) -> List[DBConflict]:
        return self.db.query(DBConflict).all()

    def get_review_queue(self, status: Optional[str] = None) -> List[DBReviewQueue]:
        q = self.db.query(DBReviewQueue)
        if status:
            q = q.filter(DBReviewQueue.status == status)
        return q.all()

    def update_review_item(self, queue_id: str, status: str, corrected_value: Optional[str] = None, notes: Optional[str] = None):
        item = self.db.query(DBReviewQueue).filter(DBReviewQueue.queue_id == queue_id).first()
        if item:
            item.status = status
            if corrected_value is not None:
                item.corrected_value = corrected_value
            if notes is not None:
                item.reviewer_notes = notes
            self.db.commit()
            return item
        return None
