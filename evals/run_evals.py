from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

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
    failures: list[dict[str, str]] = []
    supported_total = 0
    supported_top1_correct = 0
    supported_with_citation = 0
    unsupported_total = 0
    unsupported_refused = 0

    for case in cases:
        results = retrieve_relevant_chunks(case["question"])
        behavior = case["expected_behavior"]

        if behavior == "answer":
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
            if not results:
                unsupported_refused += 1
            else:
                top_result = results[0].chunk
                failures.append(
                    {
                        "id": case["id"],
                        "reason": (
                            "expected refusal, got "
                            f"{top_result.document} / {top_result.section}"
                        ),
                    }
                )
        else:
            raise ValueError(
                f"Unknown expected_behavior for {case.get('id', '<missing id>')}"
            )

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
