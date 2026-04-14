from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Command to run the file:
# python tests/run_evaluation.py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.evaluation import (  # noqa: E402
    evaluate_feature_from_dataset,
    get_evaluation_dataset_item,
)


if __name__ == "__main__":
    dataset_item = get_evaluation_dataset_item(
        comment_id=2,
        dataset_path=PROJECT_ROOT / "1_Data" / "agent_2.1_dataset.json",
    )
    result = evaluate_feature_from_dataset(
        comment_id=dataset_item.id,
        dataset_path=PROJECT_ROOT / "1_Data" / "agent_2.1_dataset.json",
    )

    print("Input:")
    print(json.dumps(asdict(dataset_item), indent=2))
    print("\nLLM response:")
    print(json.dumps(asdict(result), indent=2))
