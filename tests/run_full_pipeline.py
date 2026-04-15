from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Command to run the file:
# uv run python tests/run_full_pipeline.py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.extractor import get_dataset_item  # noqa: E402
from user_story_generator_agent.services.orchestrator import (  # noqa: E402
    analyze_feedback_from_dataset,
)


if __name__ == "__main__":
    dataset_item = get_dataset_item(
        comment_id=1,
        dataset_path=PROJECT_ROOT / "1_Data" / "agent_1_dataset.json",
    )
    result = analyze_feedback_from_dataset(
        comment_id=dataset_item.id,
        dataset_path=PROJECT_ROOT / "1_Data" / "agent_1_dataset.json",
    )

    print("Input:")
    print(json.dumps(asdict(dataset_item), indent=2))
    print("\nFinal Product Owner output:")
    print(json.dumps(asdict(result), indent=2))
