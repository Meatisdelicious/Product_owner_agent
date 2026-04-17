from __future__ import annotations

from user_story_generator_agent.services.orchestrator import (
    FeedbackInput,
    build_feedback_input,
)


def test_build_feedback_input_converts_payload_values():
    payload = {
        "id": "42",
        "user": "alice",
        "comment": "Please add CSV export.",
    }

    result = build_feedback_input(payload)

    assert result == FeedbackInput(
        id=42,
        user="alice",
        comment="Please add CSV export.",
    )
