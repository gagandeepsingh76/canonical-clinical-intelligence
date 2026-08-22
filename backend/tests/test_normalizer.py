import pytest
from app.models.schemas import ConditionEntity, MedicationEntity, ObservationEntity, ProcedureEntity
from app.services.normalizer import TerminologyNormalizerService

def test_terminology_normalizer():
    normalizer = TerminologyNormalizerService()

    # 1. Condition
    c = ConditionEntity(condition_id="c1", patient_id="p1", name="Right lumbar radiculopathy")
    normalizer.normalize_condition(c)
    assert c.terminology is not None
    assert c.terminology.code == "M54.16"
    assert c.terminology.mapping_confidence >= 0.85

    # 2. Medication
    m = MedicationEntity(medication_id="m1", patient_id="p1", name="Cyclobenzaprine", dose="10 mg")
    normalizer.normalize_medication(m)
    assert m.terminology is not None
    assert m.terminology.code == "205423"

    # 3. Observation
    o = ObservationEntity(observation_id="o1", patient_id="p1", category="vital-signs", name="Pain Severity Score (0-10)")
    normalizer.normalize_observation(o)
    assert o.terminology is not None
    assert o.terminology.code == "72514-3"

    # 4. Procedure
    pr = ProcedureEntity(procedure_id="pr1", patient_id="p1", name="Right L4-L5 Lumbar Microdiscectomy")
    normalizer.normalize_procedure(pr)
    assert pr.terminology is not None
    assert pr.terminology.code == "63030"
