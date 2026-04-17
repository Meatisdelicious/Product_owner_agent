from __future__ import annotations

import json

import pytest

from user_story_generator_agent.services.scoring import (
    ScoringInput,
    get_scoring_dataset_item,
    load_scoring_dataset,
)


def test_load_scoring_dataset_parses_input_items(tmp_path):
    dataset_path = tmp_path / "scoring_dataset.json"
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
                        "impact": "4",
                        "urgency": "3",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_scoring_dataset(dataset_path)

    assert result == [
        ScoringInput(
            id=1,
            user="alice",
            comment="Please add CSV export.",
            feature_type="feature_request",
            feature="CSV export",
            impact="4",
            urgency="3",
        )
    ]


def test_get_scoring_dataset_item_returns_matching_comment(tmp_path):
    dataset_path = tmp_path / "scoring_dataset.json"
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
                        "impact": "4",
                        "urgency": "3",
                    },
                },
                {
                    "id": 2,
                    "input": {
                        "user": "bob",
                        "comment": "Improve permissions.",
                        "feature_type": "improvement",
                        "feature": "role-based permissions",
                        "impact": "5",
                        "urgency": "4",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    result = get_scoring_dataset_item(2, dataset_path)

    assert result == ScoringInput(
        id=2,
        user="bob",
        comment="Improve permissions.",
        feature_type="improvement",
        feature="role-based permissions",
        impact="5",
        urgency="4",
    )


def test_get_scoring_dataset_item_raises_for_unknown_id(tmp_path):
    dataset_path = tmp_path / "scoring_dataset.json"
    dataset_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="No comment found with id 99"):
        get_scoring_dataset_item(99, dataset_path)
