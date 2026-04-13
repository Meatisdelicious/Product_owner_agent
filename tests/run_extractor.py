from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Command to run the file 
# python tests/run_extractor.py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.extractor import (
    extract_feature_from_dataset,
    get_dataset_item,
)


if __name__ == "__main__":
    dataset_item = get_dataset_item(
        comment_id=1,
        dataset_path=PROJECT_ROOT / "1_Data" / "comments_dataset.json",
    )
    result = extract_feature_from_dataset(
        comment_id=dataset_item.id,
        dataset_path=PROJECT_ROOT / "1_Data" / "comments_dataset.json",
    )

    print("Input comment:")
    print(dataset_item.comment)
    print("\nLLM response:")
    print(json.dumps(asdict(result), indent=2))
