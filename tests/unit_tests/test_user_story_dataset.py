from __future__ import annotations

import json

import pytest

from user_story_generator_agent.services.user_story import (
    UserStoryInput,
    get_user_story_dataset_item,
    load_user_story_dataset,
)


def test_load_user_story_dataset_parses_input_items(tmp_path):
    dataset_path = tmp_path / "user_story_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                        "feature": "CSV export",
                        "feature_type": "feature_request",
                        "impact": "4",
                        "urgency": "3",
                        "feature_recommendation_justification": (
                            "This feature helps users analyze project data."
                        ),
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_user_story_dataset(dataset_path)

    assert result == [
        UserStoryInput(
            id=1,
            user="alice",
            comment="Please add CSV export.",
            feature="CSV export",
            feature_type="feature_request",
            impact="4",
            urgency="3",
            feature_recommendation_justification=(
                "This feature helps users analyze project data."
            ),
        )
    ]


def test_get_user_story_dataset_item_returns_matching_comment(tmp_path):
    dataset_path = tmp_path / "user_story_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                        "feature": "CSV export",
                        "feature_type": "feature_request",
                        "impact": "4",
                        "urgency": "3",
                        "feature_recommendation_justification": (
                            "This feature helps users analyze project data."
                        ),
                    },
                },
                {
                    "id": 2,
                    "input": {
                        "user": "bob",
                        "comment": "Improve permissions.",
                        "feature": "role-based permissions",
                        "feature_type": "improvement",
                        "impact": "5",
                        "urgency": "4",
                        "feature_recommendation_justification": (
                            "This feature reduces access management risk."
                        ),
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    result = get_user_story_dataset_item(2, dataset_path)

    assert result == UserStoryInput(
        id=2,
        user="bob",
        comment="Improve permissions.",
        feature="role-based permissions",
        feature_type="improvement",
        impact="5",
        urgency="4",
        feature_recommendation_justification=(
            "This feature reduces access management risk."
        ),
    )


def test_get_user_story_dataset_item_raises_for_unknown_id(tmp_path):
    dataset_path = tmp_path / "user_story_dataset.json"
    dataset_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="No comment found with id 99"):
        get_user_story_dataset_item(99, dataset_path)
