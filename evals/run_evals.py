from __future__ import annotations

import argparse
import asyncio
from pathlib import Path
from typing import Any

import yaml

from app.services.chat_service import process_chat
from app.services.retrieval_service import retrieve_relevant_chunks

DEFAULT_DATASET_PATH = Path(__file__).with_name("questions.yaml")


def load_dataset(path: Path = DEFAULT_DATASET_PATH) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
        raise ValueError("Evaluation dataset must contain a cases list")
    if not isinstance(data.get("quality_gates"), dict):
        raise ValueError("Evaluation dataset must contain quality_gates")
    return data


def evaluate_dataset(path: Path = DEFAULT_DATASET_PATH) -> dict[str, Any]:
    dataset = load_dataset(path)
    cases = dataset["cases"]
    structured_cases = dataset.get("structured_cases", [])
    failures: list[dict[str, str]] = []
    supported_total = 0
    supported_top1_correct = 0
    supported_with_citation = 0
    unsupported_total = 0
    unsupported_refused = 0
    structured_total = 0
    structured_passed = 0
    calculation_total = 0
    calculation_passed = 0

    for case in cases:
        behavior = case["expected_behavior"]

        if behavior == "answer":
            results = retrieve_relevant_chunks(case["question"])
            supported_total += 1
            if results and results[0].chunk.chunk_id:
                supported_with_citation += 1

            top_result = results[0].chunk if results else None
            source_is_correct = bool(
                top_result
                and top_result.document == case["expected_document"]
                and top_result.section == case["expected_section"]
            )
            if source_is_correct:
                supported_top1_correct += 1
            else:
                actual = (
                    f"{top_result.document} / {top_result.section}"
                    if top_result
                    else "no result"
                )
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            "expected "
                            f"{case['expected_document']} / {case['expected_section']}, "
                            f"got {actual}"
                        ),
                    }
                )
        elif behavior == "refuse":
            unsupported_total += 1
            response = asyncio.run(process_chat(case["question"]))
            refusal_is_safe = (
                response.intent == "unsupported"
                and not response.sources
                and response.reservoir is None
                and response.calculation_result is None
                and not response.observations
                and not response.anomaly_flags
            )
            expected_warning = case.get("expected_warning")
            if expected_warning and expected_warning not in response.warnings:
                refusal_is_safe = False

            if refusal_is_safe:
                unsupported_refused += 1
            else:
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            "expected a safe refusal, got "
                            f"intent={response.intent}, sources={len(response.sources)}, "
                            f"observations={len(response.observations)}"
                        ),
                    }
                )
        else:
            raise ValueError(
                f"Unknown expected_behavior for {case.get('id', '<missing id>')}"
            )

    structured_report = asyncio.run(_evaluate_structured_cases(structured_cases))
    structured_total = structured_report["structured_total"]
    structured_passed = structured_report["structured_passed"]
    calculation_total = structured_report["calculation_total"]
    calculation_passed = structured_report["calculation_passed"]
    failures.extend(structured_report["failures"])

    metrics = {
        "supported_top1_accuracy": (
            supported_top1_correct / supported_total if supported_total else 0.0
        ),
        "unsupported_refusal_accuracy": (
            unsupported_refused / unsupported_total if unsupported_total else 0.0
        ),
        "citation_rate": (
            supported_with_citation / supported_total if supported_total else 0.0
        ),
        "structured_success_rate": (
            structured_passed / structured_total if structured_total else 1.0
        ),
        "calculation_check_rate": (
            calculation_passed / calculation_total if calculation_total else 1.0
        ),
    }
    gates = dataset["quality_gates"]
    passed = all(metrics[name] >= float(threshold) for name, threshold in gates.items())

    return {
        "total_cases": len(cases),
        "metrics": metrics,
        "quality_gates": gates,
        "failures": failures,
        "passed": passed,
    }


async def _evaluate_structured_cases(cases: list[dict[str, Any]]) -> dict[str, Any]:
    failures: list[dict[str, str]] = []
    structured_total = 0
    structured_passed = 0
    calculation_total = 0
    calculation_passed = 0

    for case in cases:
        structured_total += 1
        response = await process_chat(case["question"])
        case_passed = True

        expected_intent = case.get("expected_intent")
        if expected_intent and response.intent != expected_intent:
            case_passed = False
            failures.append(
                {
                    "id": case["id"],
                    "reason": (
                        f"expected intent {expected_intent}, got {response.intent}"
                    ),
                }
            )

        expected_reservoir = case.get("expected_reservoir")
        if expected_reservoir:
            actual_reservoir = response.reservoir.name if response.reservoir else None
            if actual_reservoir != expected_reservoir:
                case_passed = False
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            f"expected reservoir {expected_reservoir}, "
                            f"got {actual_reservoir}"
                        ),
                    }
                )

        min_observations = int(case.get("min_observations", 0))
        if len(response.observations) < min_observations:
            case_passed = False
            failures.append(
                {
                    "id": case["id"],
                    "reason": (
                        f"expected at least {min_observations} observations, "
                        f"got {len(response.observations)}"
                    ),
                }
            )

        min_anomaly_flags = int(case.get("min_anomaly_flags", 0))
        if len(response.anomaly_flags) < min_anomaly_flags:
            case_passed = False
            failures.append(
                {
                    "id": case["id"],
                    "reason": (
                        f"expected at least {min_anomaly_flags} anomaly flags, "
                        f"got {len(response.anomaly_flags)}"
                    ),
                }
            )

        min_sources = int(case.get("min_sources", 0))
        if len(response.sources) < min_sources:
            case_passed = False
            failures.append(
                {
                    "id": case["id"],
                    "reason": (
                        f"expected at least {min_sources} sources, "
                        f"got {len(response.sources)}"
                    ),
                }
            )

        missing_terms = [
            term
            for term in case.get("required_answer_terms", [])
            if term not in response.answer
        ]
        if missing_terms:
            case_passed = False
            failures.append(
                {
                    "id": case["id"],
                    "reason": f"answer is missing required terms: {missing_terms}",
                }
            )

        expected_quality_status = case.get("expected_quality_status")
        if expected_quality_status:
            actual_quality_status = (
                response.quality_assessment.status
                if response.quality_assessment
                else None
            )
            if actual_quality_status != expected_quality_status:
                case_passed = False
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            f"expected quality status {expected_quality_status}, "
                            f"got {actual_quality_status}"
                        ),
                    }
                )

        if "expected_calculation_metric" in case:
            calculation_total += 1
            calculation = response.calculation_result
            expected_metric = case["expected_calculation_metric"]
            expected_value = float(case["expected_value"])
            tolerance = float(case.get("tolerance", 0.01))
            calculation_matches = bool(
                calculation
                and calculation.metric == expected_metric
                and abs(calculation.value - expected_value) <= tolerance
            )
            if calculation_matches:
                calculation_passed += 1
            else:
                case_passed = False
                actual = (
                    f"{calculation.metric}={calculation.value}"
                    if calculation
                    else "no calculation"
                )
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            f"expected calculation {expected_metric}="
                            f"{expected_value}, got {actual}"
                        ),
                    }
                )

        if case_passed:
            structured_passed += 1

    return {
        "structured_total": structured_total,
        "structured_passed": structured_passed,
        "calculation_total": calculation_total,
        "calculation_passed": calculation_passed,
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run local reservoir methodology retrieval evaluations"
    )
    parser.add_argument(
        "--dataset",
        type=Path,
        default=DEFAULT_DATASET_PATH,
        help="Path to the YAML evaluation dataset",
    )
    args = parser.parse_args()
    report = evaluate_dataset(args.dataset)

    for failure in report["failures"]:
        print(f"FAIL {failure['id']}: {failure['reason']}")

    print(f"Cases: {report['total_cases']}")
    for name, value in report["metrics"].items():
        threshold = float(report["quality_gates"][name])
        print(f"{name}: {value:.1%} (required {threshold:.1%})")
    print("PASS" if report["passed"] else "FAIL")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
