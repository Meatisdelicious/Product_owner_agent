from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Command to run the file:
# python tests/run_scoring.py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_2.2_dataset.json"

sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.scoring import ( 
    get_scoring_dataset_item,
    score_feature_from_dataset,
)


def main() -> None:
    """Run a local feature scoring against one dataset item."""
    dataset_item = get_scoring_dataset_item(
        comment_id=3,
        dataset_path=DATASET_PATH,
    )
    result = score_feature_from_dataset(
        comment_id=dataset_item.id,
        dataset_path=DATASET_PATH,
    )

    print("Input:")
    print(json.dumps(asdict(dataset_item), indent=2))
    print("\nLLM response:")
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
