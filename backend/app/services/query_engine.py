import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models.db_models import (
    DBPatient, DBEncounter, DBDocument, DBCondition,
    DBMedication, DBObservation, DBProcedure, DBConflict,
    DBReviewQueue, DBDocumentPage
)

class ClinicalQueryEngine:
    def __init__(self, db: Session):
        self.db = db

    def query_patient_timeline(self) -> List[Dict[str, Any]]:
        """1. Complete patient timeline ordered by date."""
        timeline_events = []
        
        # Add encounters
        encounters = self.db.query(DBEncounter).all()
        for enc in encounters:
            timeline_events.append({
                "date": enc.encounter_date,
                "event_type": "Encounter",
                "category": enc.encounter_type,
                "facility": enc.facility or "Unspecified Facility",
                "provider": enc.provider,
                "description": f"{enc.encounter_type} at {enc.facility or 'Clinic'}",
                "is_historical": enc.is_historical
            })

        # Add procedures
        procedures = self.db.query(DBProcedure).all()
        for proc in procedures:
            if proc.performed_date:
                timeline_events.append({
                    "date": proc.performed_date,
                    "event_type": "Procedure",
                    "category": proc.cpt_code or "CPT",
                    "facility": proc.location or "Medical Center",
                    "provider": proc.performer,
                    "description": f"{proc.name} - {proc.findings or 'Completed'}",
                    "is_historical": False
                })

        # Sort timeline chronologically (converting MM/DD/YYYY to sortable key)
        def parse_sort_key(ev):
            d = ev["date"]
            if not d:
                return "0000-00-00"
            if "/" in d:
                parts = d.split("/")
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            return d

        timeline_events.sort(key=parse_sort_key)
        return timeline_events

    def query_diagnoses_with_provenance(self) -> List[Dict[str, Any]]:
        """2. All diagnoses and the source pages where they were found."""
        conditions = self.db.query(DBCondition).all()
        results = []
        for c in conditions:
            pages = []
            if c.provenance:
                for p in c.provenance:
                    if p.get("source_page") and p.get("source_page") not in pages:
                        pages.append(p.get("source_page"))
            results.append({
                "condition_id": c.condition_id,
                "diagnosis_name": c.name,
                "icd10_code": c.icd10_code,
                "icd10_display": c.icd10_display,
                "clinical_status": c.clinical_status,
                "is_historical": c.is_historical,
                "source_pages": sorted(pages),
                "confidence": c.confidence
            })
        return results

    def query_medication_history(self) -> List[Dict[str, Any]]:
        """3. Medication history with active, discontinued, and adverse reaction information."""
        meds = self.db.query(DBMedication).all()
        results = []
        for m in meds:
            results.append({
                "medication_id": m.medication_id,
                "name": m.name,
                "rxnorm_code": m.rxnorm_code,
                "rxnorm_display": m.rxnorm_display,
                "dose": m.dose,
                "route": m.route,
                "frequency": m.frequency,
                "status": m.status,
                "prescribed_date": m.prescribed_date,
                "dispensed_date": m.dispensed_date,
                "indication": m.indication,
                "adverse_reactions": m.adverse_reactions or "None reported",
                "provenance": m.provenance
            })
        return results

    def query_abnormal_observations(self) -> List[Dict[str, Any]]:
        """4. All abnormal or clinically significant observations in chronological order."""
        obs = self.db.query(DBObservation).filter(
            (DBObservation.interpretation == "abnormal") | 
            (DBObservation.value_numeric >= 4.0) |
            (DBObservation.name.like("%Straight Leg%")) |
            (DBObservation.name.like("%EHL%"))
        ).all()

        results = []
        for o in obs:
            results.append({
                "observation_id": o.observation_id,
                "effective_date": o.effective_date,
                "name": o.name,
                "value": o.value_string or str(o.value_numeric),
                "unit": o.unit,
                "reference_range": o.reference_range,
                "interpretation": o.interpretation or "abnormal",
                "provenance": o.provenance
            })

        def parse_date(item):
            d = item.get("effective_date", "")
            if not d:
                return "0000-00-00"
            if "/" in d:
                parts = d.split("/")
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            return d

        results.sort(key=parse_date)
        return results

    def query_lumbar_radiculopathy_records(self) -> Dict[str, Any]:
        """5. All records related to lumbar radiculopathy or L4-L5 pathology."""
        matching_conditions = self.db.query(DBCondition).filter(
            (DBCondition.name.like("%radiculopathy%")) | 
            (DBCondition.name.like("%L4-L5%")) |
            (DBCondition.name.like("%disc%")) |
            (DBCondition.name.like("%lumb%"))
        ).all()

        matching_procedures = self.db.query(DBProcedure).filter(
            (DBProcedure.name.like("%microdiscectomy%")) |
            (DBProcedure.name.like("%transforaminal%")) |
            (DBProcedure.name.like("%mri lumbar%")) |
            (DBProcedure.name.like("%radiographs%"))
        ).all()

        matching_observations = self.db.query(DBObservation).filter(
            (DBObservation.name.like("%Leg Raise%")) |
            (DBObservation.name.like("%EHL%")) |
            (DBObservation.name.like("%Pain%"))
        ).all()

        return {
            "query_topic": "Lumbar Radiculopathy & L4-L5 Pathology",
            "conditions": [
                {
                    "name": c.name,
                    "icd10": c.icd10_code,
                    "status": c.clinical_status,
                    "provenance": c.provenance
                } for c in matching_conditions
            ],
            "procedures": [
                {
                    "name": p.name,
                    "date": p.performed_date,
                    "cpt": p.cpt_code,
                    "findings": p.findings
                } for p in matching_procedures
            ],
            "observations": [
                {
                    "name": o.name,
                    "date": o.effective_date,
                    "value": o.value_string or str(o.value_numeric),
                    "interpretation": o.interpretation
                } for o in matching_observations
            ]
        }

    def query_conflicts_requiring_review(self) -> List[Dict[str, Any]]:
        """6. Show all conflicts requiring review."""
        conflicts = self.db.query(DBConflict).filter(DBConflict.requires_review == True).all()
        return [
            {
                "conflict_id": c.conflict_id,
                "field": c.field,
                "candidate_values": c.candidate_values,
                "source_pages": c.source_pages,
                "resolution": c.resolution,
                "resolution_reason": c.resolution_reason,
                "status": c.status
            } for c in conflicts
        ]

    def query_page_extracted_info(self, page_number: int) -> Dict[str, Any]:
        """7. Show all information extracted from a particular source page."""
        page = self.db.query(DBDocumentPage).filter(DBDocumentPage.page_number == page_number).first()
        if not page:
            return {"page_number": page_number, "error": "Page not found"}

        # Find matching entities with provenance on this page
        matching_conditions = []
        for c in self.db.query(DBCondition).all():
            if c.provenance and any(p.get("source_page") == page_number for p in c.provenance):
                matching_conditions.append({"name": c.name, "icd10": c.icd10_code})

        matching_meds = []
        for m in self.db.query(DBMedication).all():
            if m.provenance and any(p.get("source_page") == page_number for p in m.provenance):
                matching_meds.append({"name": m.name, "dose": m.dose, "status": m.status})

        matching_procs = []
        for pr in self.db.query(DBProcedure).all():
            if pr.provenance and any(p.get("source_page") == page_number for p in pr.provenance):
                matching_procs.append({"name": pr.name, "cpt": pr.cpt_code, "findings": pr.findings})

        matching_obs = []
        for o in self.db.query(DBObservation).all():
            if o.provenance and any(p.get("source_page") == page_number for p in o.provenance):
                matching_obs.append({"name": o.name, "value": o.value_string or str(o.value_numeric)})

        return {
            "page_number": page_number,
            "predicted_document_type": page.predicted_document_type,
            "is_duplicate": page.is_duplicate,
            "duplicate_of": page.duplicate_of,
            "extracted_conditions": matching_conditions,
            "extracted_medications": matching_meds,
            "extracted_procedures": matching_procs,
            "extracted_observations": matching_obs,
            "raw_text_preview": page.cleaned_text[:500] + "..." if len(page.cleaned_text) > 500 else page.cleaned_text
        }

    def query_procedure_history(self) -> List[Dict[str, Any]]:
        """8. Show surgical and procedure history."""
        procs = self.db.query(DBProcedure).all()
        return [
            {
                "procedure_id": p.procedure_id,
                "name": p.name,
                "cpt_code": p.cpt_code,
                "performed_date": p.performed_date,
                "performer": p.performer,
                "location": p.location,
                "findings": p.findings,
                "provenance": p.provenance
            } for p in procs
        ]

    def query_pain_progression(self) -> List[Dict[str, Any]]:
        """9. Show progression of pain scores over time."""
        pain_obs = self.db.query(DBObservation).filter(
            DBObservation.name.like("%Pain%")
        ).all()

        results = []
        for o in pain_obs:
            results.append({
                "effective_date": o.effective_date,
                "score_string": o.value_string,
                "score_numeric": o.value_numeric,
                "provenance": o.provenance
            })

        def parse_date(item):
            d = item.get("effective_date", "")
            if not d:
                return "0000-00-00"
            if "/" in d:
                parts = d.split("/")
                if len(parts) == 3:
                    return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
            return d

        results.sort(key=parse_date)
        return results
