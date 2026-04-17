from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path

# Commands to run the file:
# python tests/inference/inference_full_pipeline.py

# Example input string:
# We need role-based permissions because managing access across large teams is
# risky right now. Admin control is not granular enough.

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.orchestrator import (  # noqa: E402
    FeedbackInput,
    analyze_feedback,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run the full Product Owner pipeline from a user feedback comment."
    )
    parser.add_argument(
        "comment",
        nargs="*",
    )
    args = parser.parse_args()

    comment = " ".join(args.comment).strip()
    if not comment:
        comment = input("Enter a user feedback comment: ").strip()

    if not comment:
        raise SystemExit("No comment provided.")

    feedback = FeedbackInput(
        id=1,
        user="manual_input",
        comment=comment,
    )
    result = analyze_feedback(feedback)

    print("\nInput:")
    print(json.dumps(asdict(feedback), indent=2))
    print("\nFinal Product Owner output:")
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
