from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

# Command to run the file:
# uv run python tests/evaluation/evaluate_full_pipeline.py


# Running evaluation on a dataset of 30 pairs (comment-expected output).
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.orchestrator import (  
    FeedbackInput,
    ProductOwnerAgent,
)


DEFAULT_DATASET_PATH = PROJECT_ROOT / "1_Data" / "full_pipeline_large_dataset.json"
TEXT_OVERLAP_THRESHOLDS = {
    "feature": 0.5,
    "impact_justification": 0.4,
    "urgency_justification": 0.4,
    "feature_recommendation_justification": 0.4,
    "user_story": 0.4,
}
COMPLEXITY_FACTOR_FIELDS = [
    "backend_changes",
    "frontend_changes",
    "data_model_changes",
    "security_constraints",
    "integration_dependencies",
]


def main() -> None:
    """Evaluate the full pipeline against the configured dataset."""
    dataset = _load_dataset(DEFAULT_DATASET_PATH)
    agent = ProductOwnerAgent()
    results = []

    for item in dataset:
        feedback = FeedbackInput(
            id=int(item["id"]),
            user=str(item["input"]["user"]),
            comment=str(item["input"]["comment"]),
        )
        expected = item["expected_output"]
        predicted = asdict(agent.analyze(feedback))
        results.append(_evaluate_item(item["id"], expected, predicted))

    _print_report(results)


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    """Load evaluation cases from a JSON dataset file."""
    with path.open(encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def _evaluate_item(item_id: int,expected: dict[str, Any],predicted: dict[str, Any]) -> dict[str, Any]:
    """Compare one expected output with one pipeline prediction."""
    exact_fields = [
        "feature_type",
        "moscow_category_result",
        "development_complexity_estimation",
    ]
    score_fields = ["impact", "urgency"]

    exact_results = {
        field: _normalize(expected[field]) == _normalize(predicted[field])
        for field in exact_fields
    }
    score_results = {
        field: {
            "exact": _to_float(expected[field]) == _to_float(predicted[field]),
            "absolute_error": abs(
                _to_float(expected[field]) - _to_float(predicted[field])
            ),
        }
        for field in score_fields
    }
    priority_score_error = abs(
        _to_float(expected["feature_priority_score"])
        - _to_float(predicted["feature_priority_score"])
    )
    complexity_results = _evaluate_complexity_factors(
        expected["complexity_factors"],
        predicted["complexity_factors"],
    )
    text_results = {
        field: {
            "overlap": _token_overlap(expected[field], predicted[field]),
            "pass": _token_overlap(expected[field], predicted[field])
            >= TEXT_OVERLAP_THRESHOLDS[field],
        }
        for field in TEXT_OVERLAP_THRESHOLDS
    }
    user_story_format_pass = _user_story_format_pass(predicted["user_story"])
    acceptance_criteria_results = _evaluate_acceptance_criteria(
        predicted["feature_acceptance_criteria"]
    )

    item_pass = (
        all(exact_results.values())
        and all(result["exact"] for result in score_results.values())
        and priority_score_error <= 0.1
        and complexity_results["accuracy"] >= 0.8
        and user_story_format_pass
        and acceptance_criteria_results["format_pass"]
    )

    return {
        "id": item_id,
        "pass": item_pass,
        "exact": exact_results,
        "scores": score_results,
        "priority_score_error": priority_score_error,
        "complexity": complexity_results,
        "text": text_results,
        "user_story_format_pass": user_story_format_pass,
        "acceptance_criteria": acceptance_criteria_results,
    }


def _evaluate_complexity_factors(expected: dict[str, Any],predicted: dict[str, Any]) -> dict[str, Any]:
    """Calculate per-field and overall accuracy for complexity factors."""
    field_results = {
        field: int(expected[field]) == int(predicted[field])
        for field in COMPLEXITY_FACTOR_FIELDS
    }
    correct_count = sum(1 for result in field_results.values() if result)
    return {
        "fields": field_results,
        "accuracy": correct_count / len(COMPLEXITY_FACTOR_FIELDS),
    }


def _evaluate_acceptance_criteria(criteria: list[str]) -> dict[str, Any]:
    """Check whether acceptance criteria match the expected output format."""
    count_pass = len(criteria) == 3
    prefix_pass = all(
        criterion.startswith("A user can") or criterion.startswith("The system")
        for criterion in criteria
    )
    word_limit_pass = all(_word_count(criterion) <= 20 for criterion in criteria)
    no_empty_pass = all(bool(criterion.strip()) for criterion in criteria)
    return {
        "count_pass": count_pass,
        "prefix_pass": prefix_pass,
        "word_limit_pass": word_limit_pass,
        "no_empty_pass": no_empty_pass,
        "format_pass": count_pass and prefix_pass and word_limit_pass and no_empty_pass,
    }


def _print_report(results: list[dict[str, Any]]) -> None:
    """Print aggregate evaluation metrics and failure details."""
    total = len(results)
    print("Full Pipeline Evaluation :")
    print("-------------------------")
    print(f"test set size = {total}")
    print()

    _print_exact_metric(results, "feature_type", "feature_type_accuracy")
    _print_exact_metric(results, "moscow_category_result", "moscow_category_accuracy")
    _print_exact_metric(
        results,
        "development_complexity_estimation",
        "development_complexity_accuracy",
    )
    print()

    _print_score_metric(results, "impact")
    _print_score_metric(results, "urgency")
    print(
        "priority_score_mae: "
        f"{_average(result['priority_score_error'] for result in results):.2f}"
    )
    print()

    complexity_accuracy = _average(
        result["complexity"]["accuracy"] for result in results
    )
    print(f"complexity_factor_accuracy: {_percent(complexity_accuracy)}")
    for field in COMPLEXITY_FACTOR_FIELDS:
        field_accuracy = _average(
            1.0 if result["complexity"]["fields"][field] else 0.0
            for result in results
        )
        print(f"{field}_accuracy: {_percent(field_accuracy)}")
    print()

    for field in TEXT_OVERLAP_THRESHOLDS:
        overlap = _average(result["text"][field]["overlap"] for result in results)
        pass_rate = _average(
            1.0 if result["text"][field]["pass"] else 0.0
            for result in results
        )
        print(f"{field}_token_overlap_avg: {overlap:.2f}")
        print(f"{field}_token_overlap_pass_rate: {_percent(pass_rate)}")
    print()

    user_story_format_rate = _average(
        1.0 if result["user_story_format_pass"] else 0.0 for result in results
    )
    acceptance_format_rate = _average(
        1.0 if result["acceptance_criteria"]["format_pass"] else 0.0
        for result in results
    )
    end_to_end_pass_rate = _average(
        1.0 if result["pass"] else 0.0 for result in results
    )
    print(f"user_story_format_pass_rate: {_percent(user_story_format_rate)}")
    print(f"acceptance_criteria_format_pass_rate: {_percent(acceptance_format_rate)}")
    print(f"end_to_end_pass_rate: {_percent(end_to_end_pass_rate)}")

    failures = [result for result in results if not result["pass"]]
    if failures:
        print()
        print("Failures :")
        print("---------")
        for failure in failures:
            print(f"- id={failure['id']}: {_failure_reasons(failure)}")


def _print_exact_metric(results: list[dict[str, Any]],field: str,label: str) -> None:
    """Print accuracy for a field that must match exactly."""
    accuracy = _average(1.0 if result["exact"][field] else 0.0 for result in results)
    print(f"{label}: {_percent(accuracy)}")


def _print_score_metric(results: list[dict[str, Any]], field: str) -> None:
    """Print exact-match accuracy and mean absolute error for a numeric score."""
    exact_accuracy = _average(
        1.0 if result["scores"][field]["exact"] else 0.0 for result in results
    )
    mae = _average(result["scores"][field]["absolute_error"] for result in results)
    print(f"{field}_exact_accuracy: {_percent(exact_accuracy)}")
    print(f"{field}_mae: {mae:.2f}")


def _failure_reasons(result: dict[str, Any]) -> str:
    """Build a readable summary of why one evaluation item failed."""
    reasons = []
    for field, passed in result["exact"].items():
        if not passed:
            reasons.append(f"{field} mismatch")
    for field, score_result in result["scores"].items():
        if not score_result["exact"]:
            reasons.append(f"{field} mismatch")
    if result["priority_score_error"] > 0.1:
        reasons.append("priority score mismatch")
    if result["complexity"]["accuracy"] < 0.8:
        reasons.append("complexity factor accuracy below 80%")
    for field, text_result in result["text"].items():
        if not text_result["pass"]:
            reasons.append(f"{field} token overlap below threshold")
    if not result["user_story_format_pass"]:
        reasons.append("user story format invalid")
    if not result["acceptance_criteria"]["format_pass"]:
        reasons.append("acceptance criteria format invalid")
    return ", ".join(reasons)


def _user_story_format_pass(value: str) -> bool:
    """Return whether a user story follows the expected sentence structure."""
    normalized = value.strip()
    return (
        normalized.startswith("As ")
        and "I want" in normalized
        and "so that" in normalized
        and normalized.endswith(".")
    )


def _token_overlap(expected: str, predicted: str) -> float:
    """Calculate the share of expected tokens present in the prediction."""
    expected_tokens = set(_tokens(expected))
    predicted_tokens = set(_tokens(predicted))
    if not expected_tokens:
        return 1.0 if not predicted_tokens else 0.0
    return len(expected_tokens & predicted_tokens) / len(expected_tokens)


def _tokens(value: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", value.lower())


def _normalize(value: Any) -> str:
    return str(value).strip().lower()


def _to_float(value: Any) -> float:
    return float(value)


def _word_count(value: str) -> int:
    return len(re.findall(r"\b\S+\b", value))


def _average(values: Any) -> float:
    value_list = list(values)
    if not value_list:
        return 0.0
    return sum(value_list) / len(value_list)


def _percent(value: float) -> str:
    return f"{value * 100:.1f}%"


if __name__ == "__main__":
    main()
