import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List
from app.config import settings
from app.models.schemas import (
    ConditionEntity, MedicationEntity, ObservationEntity,
    ProcedureEntity, TerminologyMapping
)

class TerminologyNormalizerService:
    def __init__(self):
        self.icd10_dict: Dict[str, Any] = self._load_json(settings.TERMINOLOGY_DIR / "icd10.json")
        self.rxnorm_dict: Dict[str, Any] = self._load_json(settings.TERMINOLOGY_DIR / "rxnorm.json")
        self.loinc_dict: Dict[str, Any] = self._load_json(settings.TERMINOLOGY_DIR / "loinc.json")
        self.cpt_dict: Dict[str, Any] = self._load_json(settings.TERMINOLOGY_DIR / "cpt.json")

    @staticmethod
    def _load_json(file_path: Path) -> Dict[str, Any]:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    @staticmethod
    def _matches_synonym(syn_low: str, query: str) -> Optional[float]:
        if syn_low == query:
            return 1.0
        if len(syn_low) <= 3:
            if re.search(r"\b" + re.escape(syn_low) + r"\b", query):
                return 0.92
            return None
        if syn_low in query or query in syn_low:
            return 0.90
        return None

    def normalize_condition_term(self, term: str) -> Optional[TerminologyMapping]:
        query = term.lower().strip()
        system = "http://hl7.org/fhir/sid/icd-10-cm"
        best_code = None
        best_display = None
        best_conf = 0.0

        for code, data in self.icd10_dict.items():
            disp = data["display"].lower()
            if query == disp:
                best_code = code
                best_display = data["display"]
                best_conf = 1.0
                break
            for syn in data.get("synonyms", []):
                conf = self._matches_synonym(syn.lower(), query)
                if conf and conf > best_conf:
                    best_code = code
                    best_display = data["display"]
                    best_conf = conf
            if best_conf == 1.0:
                break

        if best_code:
            return TerminologyMapping(
                original_text=term,
                system=system,
                code=best_code,
                display=best_display,
                mapping_confidence=round(best_conf, 2)
            )
        return None

    def normalize_medication_term(self, term: str) -> Optional[TerminologyMapping]:
        query = term.lower().strip()
        system = "http://www.nlm.nih.gov/research/umls/rxnorm"
        best_code = None
        best_display = None
        best_conf = 0.0

        for code, data in self.rxnorm_dict.items():
            disp = data["display"].lower()
            gen = data.get("generic_name", "").lower()
            if query == disp or query == gen:
                best_code = code
                best_display = data["display"]
                best_conf = 1.0
                break
            for syn in data.get("synonyms", []):
                conf = self._matches_synonym(syn.lower(), query)
                if conf and conf > best_conf:
                    best_code = code
                    best_display = data["display"]
                    best_conf = conf
            if best_conf == 1.0:
                break

        if best_code:
            return TerminologyMapping(
                original_text=term,
                system=system,
                code=best_code,
                display=best_display,
                mapping_confidence=round(best_conf, 2)
            )
        return None

    def normalize_observation_term(self, term: str) -> Optional[TerminologyMapping]:
        query = term.lower().strip()
        system = "http://loinc.org"
        best_code = None
        best_display = None
        best_conf = 0.0

        for code, data in self.loinc_dict.items():
            disp = data["display"].lower()
            if query == disp:
                best_code = code
                best_display = data["display"]
                best_conf = 1.0
                break
            for syn in data.get("synonyms", []):
                conf = self._matches_synonym(syn.lower(), query)
                if conf and conf > best_conf:
                    best_code = code
                    best_display = data["display"]
                    best_conf = conf
            if best_conf == 1.0:
                break

        if best_code:
            return TerminologyMapping(
                original_text=term,
                system=system,
                code=best_code,
                display=best_display,
                mapping_confidence=round(best_conf, 2)
            )
        return None

    def normalize_procedure_term(self, term: str) -> Optional[TerminologyMapping]:
        query = term.lower().strip()
        system = "http://www.ama-assn.org/go/cpt"
        best_code = None
        best_display = None
        best_conf = 0.0

        for code, data in self.cpt_dict.items():
            disp = data["display"].lower()
            if query == disp:
                best_code = code
                best_display = data["display"]
                best_conf = 1.0
                break
            for syn in data.get("synonyms", []):
                conf = self._matches_synonym(syn.lower(), query)
                if conf and conf > best_conf:
                    best_code = code
                    best_display = data["display"]
                    best_conf = conf
            if best_conf == 1.0:
                break

        if best_code:
            return TerminologyMapping(
                original_text=term,
                system=system,
                code=best_code,
                display=best_display,
                mapping_confidence=round(best_conf, 2)
            )
        return None

    @staticmethod
    def normalize_unit(unit_str: str) -> Optional[TerminologyMapping]:
        system = "http://unitsofmeasure.org"
        u = unit_str.strip().lower()
        mapping = {
            "mm[hg]": ("mm[Hg]", "Millimeter of mercury"),
            "mmhg": ("mm[Hg]", "Millimeter of mercury"),
            "bpm": ("/min", "Per minute"),
            "/min": ("/min", "Per minute"),
            "%": ("%", "Percent"),
            "percent": ("%", "Percent"),
            "deg": ("deg", "Degree (angle)"),
            "degrees": ("deg", "Degree (angle)"),
            "°": ("deg", "Degree (angle)"),
            "mg": ("mg", "Milligram"),
            "ml": ("mL", "Milliliter"),
            "{score}": ("{score}", "Score"),
            "score": ("{score}", "Score")
        }
        if u in mapping:
            code, disp = mapping[u]
            return TerminologyMapping(
                original_text=unit_str,
                system=system,
                code=code,
                display=disp,
                mapping_confidence=1.0
            )
        return None

    def normalize_condition(self, condition: ConditionEntity) -> ConditionEntity:
        mapping = self.normalize_condition_term(condition.name)
        if mapping:
            condition.terminology = mapping
        else:
            condition.terminology = TerminologyMapping(
                original_text=condition.name,
                system="http://hl7.org/fhir/sid/icd-10-cm",
                code=None,
                display=None,
                mapping_confidence=0.0,
                unmapped_reason="No confident ICD-10 mapping found in standard dictionary"
            )
        return condition

    def normalize_medication(self, medication: MedicationEntity) -> MedicationEntity:
        mapping = self.normalize_medication_term(medication.name)
        if mapping:
            medication.terminology = mapping
        else:
            medication.terminology = TerminologyMapping(
                original_text=medication.name,
                system="http://www.nlm.nih.gov/research/umls/rxnorm",
                code=None,
                display=None,
                mapping_confidence=0.0,
                unmapped_reason="No confident RxNorm code matched"
            )
        return medication

    def normalize_observation(self, observation: ObservationEntity) -> ObservationEntity:
        mapping = self.normalize_observation_term(observation.name)
        if mapping:
            observation.terminology = mapping
        else:
            observation.terminology = TerminologyMapping(
                original_text=observation.name,
                system="http://loinc.org",
                code=None,
                display=None,
                mapping_confidence=0.0,
                unmapped_reason="No standard LOINC code mapping"
            )
        return observation

    def normalize_procedure(self, procedure: ProcedureEntity) -> ProcedureEntity:
        mapping = self.normalize_procedure_term(procedure.name)
        if mapping:
            procedure.terminology = mapping
        else:
            procedure.terminology = TerminologyMapping(
                original_text=procedure.name,
                system="http://www.ama-assn.org/go/cpt",
                code=None,
                display=None,
                mapping_confidence=0.0,
                unmapped_reason="No standard CPT code mapping"
            )
        return procedure

    def normalize_all(
        self,
        conditions: List[ConditionEntity],
        medications: List[MedicationEntity],
        observations: List[ObservationEntity],
        procedures: List[ProcedureEntity]
    ):
        for c in conditions:
            self.normalize_condition(c)
        for m in medications:
            self.normalize_medication(m)
        for o in observations:
            self.normalize_observation(o)
        for p in procedures:
            self.normalize_procedure(p)
