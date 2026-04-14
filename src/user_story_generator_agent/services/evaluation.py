from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from user_story_generator_agent.context.criterias import (
    IMPACT_CRITERIA,
    URGENCY_CRITERIA,
)


EvaluationScore = Literal["1", "2", "3", "4", "5"]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_2.1_dataset.json"

EVALUATION_SYSTEM_PROMPT = """
You are Agent 2.1, a product feature evaluation agent.

Evaluate the extracted feature from a user comment.

Return only JSON with:
- impact: one of "1", "2", "3", "4", "5"
- urgency: one of "1", "2", "3", "4", "5"

Use the provided impact criteria and urgency criteria exactly as the scoring scale.
Do not add justifications, prioritization scores, MoSCoW categories, user stories, or explanations.
"""


@dataclass(frozen=True)
class EvaluationInput:
    id: int
    user: str
    comment: str
    feature_type: str
    feature: str


@dataclass(frozen=True)
class EvaluationOutput:
    impact: EvaluationScore
    urgency: EvaluationScore


class _EvaluationSchema(BaseModel):
    impact: EvaluationScore = Field(
        description="Impact score from 1 to 5 using the provided impact criteria."
    )
    urgency: EvaluationScore = Field(
        description="Urgency score from 1 to 5 using the provided urgency criteria."
    )


EVALUATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", EVALUATION_SYSTEM_PROMPT),
        ("user", "{payload}"),
    ]
)


class FeatureEvaluator:
    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm or self._build_default_llm()
        self.chain = EVALUATION_PROMPT | self.llm.with_structured_output(
            _EvaluationSchema
        )

    def evaluate(self, evaluation_input: EvaluationInput) -> EvaluationOutput:
        payload = self.chain.invoke(
            {"payload": _build_evaluation_prompt(evaluation_input)}
        )
        return EvaluationOutput(
            impact=payload.impact,
            urgency=payload.urgency,
        )

    def evaluate_from_dataset(
        self,
        comment_id: int,
        dataset_path: Path | str = DEFAULT_DATASET_PATH,
    ) -> EvaluationOutput:
        dataset_item = get_evaluation_dataset_item(comment_id, dataset_path)
        return self.evaluate(dataset_item)

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
            temperature=0.1,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ["MODEL_ID"],
        )


def load_evaluation_dataset(
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> list[EvaluationInput]:
    path = Path(dataset_path)
    with path.open(encoding="utf-8") as dataset_file:
        raw_items = json.load(dataset_file)

    return [_parse_dataset_item(item) for item in raw_items]


def get_evaluation_dataset_item(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> EvaluationInput:
    for item in load_evaluation_dataset(dataset_path):
        if item.id == comment_id:
            return item

    raise ValueError(f"No comment found with id {comment_id}.")


def evaluate_feature_from_dataset(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    llm: Any | None = None,
) -> EvaluationOutput:
    evaluator = FeatureEvaluator(llm=llm)
    return evaluator.evaluate_from_dataset(comment_id, dataset_path)


def _build_evaluation_prompt(evaluation_input: EvaluationInput) -> str:
    input_payload = {
        "id": evaluation_input.id,
        "user": evaluation_input.user,
        "comment": evaluation_input.comment,
        "feature_type": evaluation_input.feature_type,
        "feature": evaluation_input.feature,
    }
    return json.dumps(
        {
            "input": input_payload,
            "impact_criteria": IMPACT_CRITERIA,
            "urgency_criteria": URGENCY_CRITERIA,
        },
        indent=2,
    )


def _parse_dataset_item(item: dict[str, Any]) -> EvaluationInput:
    input_payload = item.get("input", item)
    feature_payload = (
        input_payload
        if "feature_type" in input_payload and "feature" in input_payload
        else item.get("expected_output", item)
    )

    return EvaluationInput(
        id=int(item["id"]),
        user=str(input_payload["user"]),
        comment=str(input_payload["comment"]),
        feature_type=str(feature_payload["feature_type"]),
        feature=str(feature_payload["feature"]),
    )

