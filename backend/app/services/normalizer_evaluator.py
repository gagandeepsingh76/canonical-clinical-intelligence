import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.config import settings
from app.services.normalizer import TerminologyNormalizerService

class TerminologyEvaluatorService:
    @classmethod
    def evaluate_benchmark(cls, dataset_path: Optional[str] = None) -> Dict[str, Any]:
        if dataset_path is None:
            dataset_path = settings.DATA_DIR / "terminology_eval_dataset.json"
        
        path_obj = Path(dataset_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Terminology evaluation benchmark not found at: {dataset_path}")

        with open(path_obj, "r", encoding="utf-8") as f:
            bench_data = json.load(f)

        cases = bench_data.get("cases", [])
        total_cases = len(cases)
        
        normalizer = TerminologyNormalizerService()

        correct_mappings = 0
        incorrect_mappings = 0
        unsupported_count = 0
        unsupported_correctly_unmapped = 0
        supported_count = 0
        supported_mapped_count = 0
        
        system_stats: Dict[str, Dict[str, int]] = {}
        case_results: List[Dict[str, Any]] = []

        for c in cases:
            cid = c["id"]
            term = c["source_term"]
            system = c["system"]
            exp_code = c["expected_code"]
            status = c.get("verified_status", "supported")

            if system not in system_stats:
                system_stats[system] = {
                    "total": 0,
                    "supported": 0,
                    "unsupported": 0,
                    "correct": 0,
                    "incorrect": 0,
                    "unmapped": 0
                }
            system_stats[system]["total"] += 1

            # Run normalization based on system
            pred_coding = None
            if system == "ICD-10-CM":
                pred_coding = normalizer.normalize_condition_term(term)
            elif system == "RxNorm":
                pred_coding = normalizer.normalize_medication_term(term)
            elif system == "LOINC":
                pred_coding = normalizer.normalize_observation_term(term)
            elif system == "CPT":
                pred_coding = normalizer.normalize_procedure_term(term)
            elif system == "UCUM":
                pred_coding = TerminologyNormalizerService.normalize_unit(term)

            pred_code = pred_coding.code if pred_coding else None
            pred_display = pred_coding.display if pred_coding else None

            is_correct = False
            if status == "supported":
                supported_count += 1
                system_stats[system]["supported"] += 1
                if pred_code is not None:
                    supported_mapped_count += 1
                    if pred_code == exp_code:
                        correct_mappings += 1
                        system_stats[system]["correct"] += 1
                        is_correct = True
                    else:
                        incorrect_mappings += 1
                        system_stats[system]["incorrect"] += 1
                else:
                    system_stats[system]["unmapped"] += 1
            else:
                # Unsupported case
                unsupported_count += 1
                system_stats[system]["unsupported"] += 1
                if pred_code is None:
                    unsupported_correctly_unmapped += 1
                    is_correct = True
                else:
                    incorrect_mappings += 1
                    system_stats[system]["incorrect"] += 1

            case_results.append({
                "id": cid,
                "source_term": term,
                "system": system,
                "expected_code": exp_code,
                "predicted_code": pred_code,
                "predicted_display": pred_display,
                "status": status,
                "is_correct": is_correct
            })

        # Calculate coverage and accuracy metrics
        mapping_coverage = (supported_mapped_count / supported_count * 100.0) if supported_count > 0 else 0.0
        mapping_accuracy = (correct_mappings / supported_mapped_count * 100.0) if supported_mapped_count > 0 else 0.0
        overall_accuracy = ((correct_mappings + unsupported_correctly_unmapped) / total_cases * 100.0) if total_cases > 0 else 0.0

        return {
            "total_evaluated_cases": total_cases,
            "supported_cases": supported_count,
            "unsupported_cases": unsupported_count,
            "supported_mapped_cases": supported_mapped_count,
            "correct_supported_mappings": correct_mappings,
            "incorrect_mappings": incorrect_mappings,
            "unsupported_correctly_unmapped": unsupported_correctly_unmapped,
            "mapping_coverage_percentage": round(mapping_coverage, 2),
            "exact_mapping_accuracy_percentage": round(mapping_accuracy, 2),
            "overall_accuracy_percentage": round(overall_accuracy, 2),
            "system_breakdown": system_stats,
            "detailed_case_results": case_results
        }
