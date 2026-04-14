from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field


FeatureType = Literal[
    "feature_request",
    "bug_report",
    "improvement",
]

EXTRACTOR_SYSTEM_PROMPT = """
You are Agent 1, a product feature extractor.

Extract the product feature from a user comment.

Return only JSON with:
- feature_type: one of feature_request, bug_report, improvement, question, other
- feature: a short product-focused phrase

Do not add scoring, prioritization, user stories, or explanations.
"""

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_1_dataset.json"


@dataclass(frozen=True)
class ExtractorInput:
    id: int
    user: str
    comment: str


@dataclass(frozen=True)
class ExtractorOutput:
    feature_type: FeatureType
    feature: str


class _ExtractorSchema(BaseModel):
    feature_type: FeatureType = Field(
        description="Type of product feature extracted from the comment."
    )
    feature: str = Field(description="Short product-focused phrase.")


EXTRACTOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", EXTRACTOR_SYSTEM_PROMPT),
        ("user", "Comment: {comment}"),
    ]
)


class FeatureExtractor:
    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm or self._build_default_llm()
        self.chain = EXTRACTOR_PROMPT | self.llm.with_structured_output(
            _ExtractorSchema
        )

    def extract(self, comment: str) -> ExtractorOutput:
        payload = self.chain.invoke({"comment": comment})
        return ExtractorOutput(
            feature_type=payload.feature_type,
            feature=payload.feature,
        )

    def extract_from_dataset(
        self,
        comment_id: int,
        dataset_path: Path | str = DEFAULT_DATASET_PATH,
    ) -> ExtractorOutput:
        dataset_item = get_dataset_item(comment_id, dataset_path)
        return self.extract(dataset_item.comment)

    def _build_default_llm(self) -> Any:
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            pass

        missing_env_vars = [
            env_var
            for env_var in ["OPENAI_API_KEY", "MODEL_ID"]
            if env_var not in os.environ
        ]
        if missing_env_vars:
            missing = ", ".join(missing_env_vars)
            raise RuntimeError(f"Missing required environment variable(s): {missing}.")

        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:
            raise RuntimeError(
                "The langchain-openai package is required. Install dependencies with `uv sync`."
            ) from exc

        return ChatOpenAI(
            temperature=0.2,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ["MODEL_ID"],
        )


def load_comments_dataset(
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> list[ExtractorInput]:
    path = Path(dataset_path)
    with path.open(encoding="utf-8") as dataset_file:
        raw_items = json.load(dataset_file)

    return [_parse_dataset_item(item) for item in raw_items]


def get_dataset_item(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> ExtractorInput:
    for item in load_comments_dataset(dataset_path):
        if item.id == comment_id:
            return item

    raise ValueError(f"No comment found with id {comment_id}.")


def extract_feature_from_dataset(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    llm: Any | None = None,
) -> ExtractorOutput:
    extractor = FeatureExtractor(llm=llm)
    return extractor.extract_from_dataset(comment_id, dataset_path)


def _parse_dataset_item(item: dict[str, Any]) -> ExtractorInput:
    input_payload = item.get("input", item)
    return ExtractorInput(
        id=int(item["id"]),
        user=str(input_payload["user"]),
        comment=str(input_payload["comment"]),
    )
