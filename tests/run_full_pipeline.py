from __future__ import annotations

import json
import sys
from dataclasses import asdict
from pathlib import Path

# Command to run the file:
# python tests/run_full_pipeline.py

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_1_dataset.json"

sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.extractor import get_dataset_item  
from user_story_generator_agent.services.orchestrator import ( 
    analyze_feedback_from_dataset,
)


def main() -> None:
    """Run the full pipeline against one dataset item."""
    dataset_item = get_dataset_item(
        comment_id=3,
        dataset_path=DATASET_PATH,
    )
    result = analyze_feedback_from_dataset(
        comment_id=dataset_item.id,
        dataset_path=DATASET_PATH,
    )

    print("Input:")
    print(json.dumps(asdict(dataset_item), indent=2))
    print("\nFinal Product Owner output:")
    print(json.dumps(asdict(result), indent=2))


if __name__ == "__main__":
    main()
