from __future__ import annotations

import json

import pytest

from user_story_generator_agent.services.extractor import (
    ExtractorInput,
    get_dataset_item,
    load_comments_dataset,
)


def test_load_comments_dataset_parses_input_items(tmp_path):
    dataset_path = tmp_path / "extractor_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                    },
                }
            ]
        ),
        encoding="utf-8",
    )

    result = load_comments_dataset(dataset_path)

    assert result == [
        ExtractorInput(
            id=1,
            user="alice",
            comment="Please add CSV export.",
        )
    ]


def test_get_dataset_item_returns_matching_comment(tmp_path):
    dataset_path = tmp_path / "extractor_dataset.json"
    dataset_path.write_text(
        json.dumps(
            [
                {
                    "id": 1,
                    "input": {
                        "user": "alice",
                        "comment": "Please add CSV export.",
                    },
                },
                {
                    "id": 2,
                    "input": {
                        "user": "bob",
                        "comment": "Role-based permissions are needed.",
                    },
                },
            ]
        ),
        encoding="utf-8",
    )

    result = get_dataset_item(2, dataset_path)

    assert result == ExtractorInput(
        id=2,
        user="bob",
        comment="Role-based permissions are needed.",
    )


def test_get_dataset_item_raises_for_unknown_id(tmp_path):
    dataset_path = tmp_path / "extractor_dataset.json"
    dataset_path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="No comment found with id 99"):
        get_dataset_item(99, dataset_path)
