from typing import List, Dict
from app.models.schemas import ConditionEntity, MedicationEntity, ProcedureEntity, ProvenanceRecord

class DeduplicationService:
    @staticmethod
    def deduplicate_conditions(conditions: List[ConditionEntity]) -> List[ConditionEntity]:
        canonical_map: Dict[str, ConditionEntity] = {}

        for cond in conditions:
            # Key based on normalized code or lower concept name and historical flag
            key = f"{cond.name.lower()}_{cond.is_historical}"
            if cond.terminology and cond.terminology.code:
                key = f"{cond.terminology.code}_{cond.is_historical}"

            if key not in canonical_map:
                canonical_map[key] = cond
            else:
                existing = canonical_map[key]
                # Merge provenance
                for p in cond.provenance:
                    if not any(ep.source_page == p.source_page and ep.source_document_id == p.source_document_id for ep in existing.provenance):
                        existing.provenance.append(p)
                
                # Keep earliest onset date or most detailed status
                if cond.onset_date and (not existing.onset_date or cond.onset_date < existing.onset_date):
                    existing.onset_date = cond.onset_date
                if cond.clinical_status == "resolved" and existing.clinical_status == "active":
                    existing.clinical_status = "resolved"

        return list(canonical_map.values())

    @staticmethod
    def deduplicate_medications(medications: List[MedicationEntity]) -> List[MedicationEntity]:
        canonical_map: Dict[str, MedicationEntity] = {}

        for med in medications:
            # Key based on medication name + dose
            key = f"{med.name.lower()}_{med.dose}"
            if med.terminology and med.terminology.code:
                key = f"{med.terminology.code}_{med.dose}"

            if key not in canonical_map:
                canonical_map[key] = med
            else:
                existing = canonical_map[key]
                # Merge provenance
                for p in med.provenance:
                    if not any(ep.source_page == p.source_page and ep.source_document_id == p.source_document_id for ep in existing.provenance):
                        existing.provenance.append(p)
                
                # Update status if active vs discontinued
                if med.status == "discontinued":
                    existing.status = "discontinued"
                if med.adverse_reactions and not existing.adverse_reactions:
                    existing.adverse_reactions = med.adverse_reactions
                if med.dispensed_date and not existing.dispensed_date:
                    existing.dispensed_date = med.dispensed_date

        return list(canonical_map.values())

    @staticmethod
    def deduplicate_procedures(procedures: List[ProcedureEntity]) -> List[ProcedureEntity]:
        canonical_map: Dict[str, ProcedureEntity] = {}

        for proc in procedures:
            # Key based on procedure name + performed date
            key = f"{proc.name.lower()}_{proc.performed_date}"
            if proc.terminology and proc.terminology.code:
                key = f"{proc.terminology.code}_{proc.performed_date}"

            if key not in canonical_map:
                canonical_map[key] = proc
            else:
                existing = canonical_map[key]
                for p in proc.provenance:
                    if not any(ep.source_page == p.source_page and ep.source_document_id == p.source_document_id for ep in existing.provenance):
                        existing.provenance.append(p)

        return list(canonical_map.values())
