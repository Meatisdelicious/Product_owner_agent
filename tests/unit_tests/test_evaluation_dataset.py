from __future__ import annotations

import json

import pytest

from user_story_generator_agent.services.evaluation import (
    EvaluationInput,
    get_evaluation_dataset_item,
    load_evaluation_dataset,
)


def test_load_evaluation_dataset_parses_expected_output_feature(tmp_path):
    dataset_path = tmp_path / "evaluation_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                    },
                    "expected_output": {
                        "feature_type": "feature_request",
                        "feature": "CSV export",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_evaluation_dataset(dataset_path)

    assert result == [
        EvaluationInput(
            id=1,
            user="alice",
            comment="Please add CSV export.",
            feature_type="feature_request",
            feature="CSV export",
        )
    ]


def test_get_evaluation_dataset_item_returns_matching_comment(tmp_path):
    dataset_path = tmp_path / "evaluation_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                        "feature_type": "feature_request",
                        "feature": "CSV export",
                    },
                },
                {
                    "id": 2,
                    "input": {
                        "user": "bob",
                        "comment": "Improve permissions.",
                        "feature_type": "improvement",
                        "feature": "role-based permissions",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    result = get_evaluation_dataset_item(2, dataset_path)

    assert result == EvaluationInput(
        id=2,
        user="bob",
        comment="Improve permissions.",
        feature_type="improvement",
        feature="role-based permissions",
    )


def test_get_evaluation_dataset_item_raises_for_unknown_id(tmp_path):
    dataset_path = tmp_path / "evaluation_dataset.json"
    dataset_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="No comment found with id 99"):
        get_evaluation_dataset_item(99, dataset_path)
