import pytest
from app.config import settings
from app.services.normalizer_evaluator import TerminologyEvaluatorService

def test_terminology_eval_benchmark_loads_and_evaluates():
    res = TerminologyEvaluatorService.evaluate_benchmark()
    
    assert res["total_evaluated_cases"] >= 100
    assert res["supported_cases"] >= 80
    assert res["unsupported_cases"] >= 15
    assert res["mapping_coverage_percentage"] >= 95.0
    assert res["exact_mapping_accuracy_percentage"] >= 95.0
    assert res["overall_accuracy_percentage"] >= 95.0

def test_terminology_eval_accuracy_and_coverage_calculation():
    res = TerminologyEvaluatorService.evaluate_benchmark()
    
    # Mathematical identity verification
    assert res["supported_cases"] + res["unsupported_cases"] == res["total_evaluated_cases"]
    assert res["correct_supported_mappings"] + res["incorrect_mappings"] <= res["total_evaluated_cases"]
    assert res["supported_mapped_cases"] <= res["supported_cases"]
    
    # Breakdown verification
    assert "ICD-10-CM" in res["system_breakdown"]
    assert "RxNorm" in res["system_breakdown"]
    assert "LOINC" in res["system_breakdown"]
    assert "CPT" in res["system_breakdown"]
    assert "UCUM" in res["system_breakdown"]

def test_terminology_eval_unsupported_out_of_scope_cases():
    res = TerminologyEvaluatorService.evaluate_benchmark()
    
    # Verify that unsupported cases are tracked separately and not counted as failed supported mappings
    assert res["unsupported_correctly_unmapped"] >= 15
    
    # Check individual case results
    case_results = res["detailed_case_results"]
    unsupported = [c for c in case_results if c["status"] == "unsupported"]
    assert len(unsupported) >= 15
    assert all(c["expected_code"] is None for c in unsupported)
    assert all(c["is_correct"] is True for c in unsupported)
