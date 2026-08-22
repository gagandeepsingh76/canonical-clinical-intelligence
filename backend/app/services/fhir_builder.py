import json
import uuid
from typing import Dict, Any, List, Tuple
from app.config import settings
from app.models.schemas import (
    PatientEntity, EncounterEntity, ConditionEntity,
    MedicationEntity, AllergyEntity, ProcedureEntity,
    ObservationEntity, LogicalDocument
)

# Import official fhir.resources models
from fhir.resources.bundle import Bundle, BundleEntry
from fhir.resources.patient import Patient
from fhir.resources.encounter import Encounter
from fhir.resources.condition import Condition
from fhir.resources.observation import Observation
from fhir.resources.medicationstatement import MedicationStatement
from fhir.resources.allergyintolerance import AllergyIntolerance
from fhir.resources.procedure import Procedure
from fhir.resources.documentreference import DocumentReference

class FHIRBuilderService:
    @staticmethod
    def _clean_id(raw_id: str) -> str:
        # FHIR ID must match ^[A-Za-z0-9\-\.]+$
        return raw_id.replace("_", "-").replace(" ", "-")

    @classmethod
    def build_and_validate_bundle(
        cls,
        patient: PatientEntity,
        encounters: List[EncounterEntity],
        conditions: List[ConditionEntity],
        medications: List[MedicationEntity],
        allergies: List[AllergyEntity],
        procedures: List[ProcedureEntity],
        observations: List[ObservationEntity],
        documents: List[LogicalDocument]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        
        bundle_entries = []
        validation_errors = []
        validated_count = 0

        patient_fhir_id = cls._clean_id(patient.patient_id)

        # 1. FHIR Patient
        try:
            pat_kwargs = {
                "id": patient_fhir_id,
                "name": [
                    {
                        "use": "official",
                        "family": patient.last_name or "Unknown",
                        "given": [patient.first_name] if patient.first_name else ["Unknown"]
                    }
                ]
            }
            if patient.mrn:
                pat_kwargs["identifier"] = [
                    {
                        "system": "http://hospital.org/mrn",
                        "value": patient.mrn
                    }
                ]
            if patient.gender and patient.gender in ["male", "female", "other", "unknown"]:
                pat_kwargs["gender"] = patient.gender
            if patient.dob:
                pat_kwargs["birthDate"] = patient.dob

            fhir_pat = Patient(**pat_kwargs)
            bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{patient_fhir_id}", resource=fhir_pat))
            validated_count += 1
        except Exception as e:
            validation_errors.append({"resource_type": "Patient", "id": patient_fhir_id, "error": str(e)})

        # 2. FHIR Encounters
        for enc in encounters:
            enc_fhir_id = cls._clean_id(enc.encounter_id)
            try:
                fhir_enc = Encounter(
                    id=enc_fhir_id,
                    status="completed",
                    class_fhir=[
                        {
                            "coding": [
                                {
                                    "system": "http://terminology.hl7.org/CodeSystem/v3-ActCode",
                                    "code": "AMB",
                                    "display": "ambulatory"
                                }
                            ]
                        }
                    ],
                    subject={"reference": f"Patient/{patient_fhir_id}"},
                    serviceProvider={"display": enc.facility or "Medical Center"}
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{enc_fhir_id}", resource=fhir_enc))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "Encounter", "id": enc_fhir_id, "error": str(e)})

        # 3. FHIR Conditions
        for cond in conditions:
            cond_fhir_id = cls._clean_id(cond.condition_id)
            try:
                codings = []
                if cond.terminology and cond.terminology.code:
                    codings.append({
                        "system": cond.terminology.system,
                        "code": cond.terminology.code,
                        "display": cond.terminology.display
                    })
                
                fhir_cond = Condition(
                    id=cond_fhir_id,
                    clinicalStatus={
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-clinical",
                            "code": "resolved" if cond.clinical_status == "resolved" else "active"
                        }]
                    },
                    verificationStatus={
                        "coding": [{
                            "system": "http://terminology.hl7.org/CodeSystem/condition-ver-status",
                            "code": "confirmed"
                        }]
                    },
                    code={
                        "coding": codings if codings else None,
                        "text": cond.name
                    },
                    subject={"reference": f"Patient/{patient_fhir_id}"}
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{cond_fhir_id}", resource=fhir_cond))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "Condition", "id": cond_fhir_id, "error": str(e)})

        # 4. FHIR Medications (MedicationStatement)
        for med in medications:
            med_fhir_id = cls._clean_id(med.medication_id)
            try:
                codings = []
                if med.terminology and med.terminology.code:
                    codings.append({
                        "system": med.terminology.system,
                        "code": med.terminology.code,
                        "display": med.terminology.display
                    })

                fhir_med = MedicationStatement(
                    id=med_fhir_id,
                    status="recorded",
                    medication={
                        "concept": {
                            "coding": codings if codings else None,
                            "text": f"{med.name} {med.dose or ''}".strip()
                        }
                    },
                    subject={"reference": f"Patient/{patient_fhir_id}"},
                    dosage=[
                        {
                            "text": f"{med.dose or ''} {med.route or ''} {med.frequency or ''}".strip()
                        }
                    ]
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{med_fhir_id}", resource=fhir_med))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "MedicationStatement", "id": med_fhir_id, "error": str(e)})

        # 5. FHIR Allergies
        for alg in allergies:
            alg_fhir_id = cls._clean_id(alg.allergy_id)
            try:
                fhir_alg = AllergyIntolerance(
                    id=alg_fhir_id,
                    code={"text": alg.allergen},
                    patient={"reference": f"Patient/{patient_fhir_id}"}
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{alg_fhir_id}", resource=fhir_alg))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "AllergyIntolerance", "id": alg_fhir_id, "error": str(e)})

        # 6. FHIR Procedures
        for proc in procedures:
            proc_fhir_id = cls._clean_id(proc.procedure_id)
            try:
                codings = []
                if proc.terminology and proc.terminology.code:
                    codings.append({
                        "system": proc.terminology.system,
                        "code": proc.terminology.code,
                        "display": proc.terminology.display
                    })

                fhir_proc = Procedure(
                    id=proc_fhir_id,
                    status="completed",
                    code={
                        "coding": codings if codings else None,
                        "text": proc.name
                    },
                    subject={"reference": f"Patient/{patient_fhir_id}"}
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{proc_fhir_id}", resource=fhir_proc))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "Procedure", "id": proc_fhir_id, "error": str(e)})

        # 7. FHIR Observations
        for obs in observations:
            obs_fhir_id = cls._clean_id(obs.observation_id)
            try:
                codings = []
                if obs.terminology and obs.terminology.code:
                    codings.append({
                        "system": obs.terminology.system,
                        "code": obs.terminology.code,
                        "display": obs.terminology.display
                    })

                obs_kwargs = {
                    "id": obs_fhir_id,
                    "status": "final",
                    "code": {
                        "coding": codings if codings else None,
                        "text": obs.name
                    },
                    "subject": {"reference": f"Patient/{patient_fhir_id}"}
                }

                if obs.value_numeric is not None:
                    obs_kwargs["valueQuantity"] = {
                        "value": obs.value_numeric,
                        "unit": obs.unit or "{score}",
                        "system": "http://unitsofmeasure.org"
                    }
                elif obs.value_string:
                    obs_kwargs["valueString"] = obs.value_string

                fhir_obs = Observation(**obs_kwargs)
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{obs_fhir_id}", resource=fhir_obs))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "Observation", "id": obs_fhir_id, "error": str(e)})

        # 8. FHIR DocumentReferences
        for doc in documents:
            doc_fhir_id = cls._clean_id(doc.document_id)
            try:
                fhir_doc = DocumentReference(
                    id=doc_fhir_id,
                    status="current",
                    type={"text": doc.title},
                    subject={"reference": f"Patient/{patient_fhir_id}"},
                    content=[
                        {
                            "attachment": {
                                "contentType": "text/plain",
                                "title": f"Pages {doc.start_page}-{doc.end_page}"
                            }
                        }
                    ]
                )
                bundle_entries.append(BundleEntry(fullUrl=f"urn:uuid:{doc_fhir_id}", resource=fhir_doc))
                validated_count += 1
            except Exception as e:
                validation_errors.append({"resource_type": "DocumentReference", "id": doc_fhir_id, "error": str(e)})

        # 9. Official FHIR Bundle Assembly
        bundle_id = f"bundle-{str(uuid.uuid4())[:8]}"
        fhir_bundle = Bundle(
            id=bundle_id,
            type="collection",
            entry=bundle_entries
        )

        bundle_dict = json.loads(fhir_bundle.json())

        # Validation statistics
        total_resources = validated_count + len(validation_errors)
        pass_rate = (validated_count / total_resources * 100.0) if total_resources > 0 else 100.0
        
        validation_report = {
            "bundle_id": bundle_id,
            "total_resources": total_resources,
            "validated_resources": validated_count,
            "failed_resources": len(validation_errors),
            "pass_rate_percentage": round(pass_rate, 2),
            "status": "PASSED" if len(validation_errors) == 0 else "PARTIAL_FAILURES",
            "errors": validation_errors
        }

        # Save to disk
        with open(settings.OUTPUT_DIR / "fhir_bundle.json", "w", encoding="utf-8") as f:
            json.dump(bundle_dict, f, indent=2)

        with open(settings.OUTPUT_DIR / "fhir_validation_report.json", "w", encoding="utf-8") as f:
            json.dump(validation_report, f, indent=2)

        return bundle_dict, validation_report
