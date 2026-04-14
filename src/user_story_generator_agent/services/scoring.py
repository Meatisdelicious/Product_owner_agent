from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from user_story_generator_agent.context.criterias import (
    IMPACT_CRITERIA,
    URGENCY_CRITERIA,
)


EvaluationScore = Literal["1", "2", "3", "4", "5"]
FEATURE_PRIORITY_IMPACT_WEIGHT = 0.4
FEATURE_PRIORITY_URGENCY_WEIGHT = 0.6

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_2.2_dataset.json"

SCORING_SYSTEM_PROMPT = """
You are Agent 2.2, a product feature scoring justification agent.

Generate justifications for the existing impact and urgency scores.

Return only JSON with:
- impact_justification: one concise sentence explaining the impact score using the comment, feature_type, feature, impact_criteria, and impact
- urgency_justification: one concise sentence explaining the urgency score using the comment, feature_type, feature, urgency_criteria, and urgency

Do not change the impact or urgency scores.
Do not add prioritization scores, MoSCoW categories, user stories, or explanations outside JSON.
"""


@dataclass(frozen=True)
class ScoringInput:
    id: int
    user: str
    comment: str
    feature_type: str
    feature: str
    impact: EvaluationScore
    urgency: EvaluationScore


@dataclass(frozen=True)
class ScoringOutput:
    impact_justification: str
    urgency_justification: str
    feature_priority_score: float


class _ScoringSchema(BaseModel):
    impact_justification: str = Field(
        description="Concise justification for the existing impact score."
    )
    urgency_justification: str = Field(
        description="Concise justification for the existing urgency score."
    )


SCORING_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SCORING_SYSTEM_PROMPT),
        ("user", "{payload}"),
    ]
)


class FeatureScorer:
    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm or self._build_default_llm()
        self.chain = SCORING_PROMPT | self.llm.with_structured_output(_ScoringSchema)

    def score(self, scoring_input: ScoringInput) -> ScoringOutput:
        payload = self.chain.invoke({"payload": _build_scoring_prompt(scoring_input)})
        return ScoringOutput(
            impact_justification=payload.impact_justification,
            urgency_justification=payload.urgency_justification,
            feature_priority_score=_calculate_feature_priority_score(scoring_input),
        )

    def score_from_dataset(
        self,
        comment_id: int,
        dataset_path: Path | str = DEFAULT_DATASET_PATH,
    ) -> ScoringOutput:
        dataset_item = get_scoring_dataset_item(comment_id, dataset_path)
        return self.score(dataset_item)

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


def load_scoring_dataset(
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> list[ScoringInput]:
    path = Path(dataset_path)
    with path.open(encoding="utf-8") as dataset_file:
        raw_items = json.load(dataset_file)

    return [_parse_dataset_item(item) for item in raw_items]


def get_scoring_dataset_item(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> ScoringInput:
    for item in load_scoring_dataset(dataset_path):
        if item.id == comment_id:
            return item

    raise ValueError(f"No comment found with id {comment_id}.")


def score_feature_from_dataset(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    llm: Any | None = None,
) -> ScoringOutput:
    scorer = FeatureScorer(llm=llm)
    return scorer.score_from_dataset(comment_id, dataset_path)


def _build_scoring_prompt(scoring_input: ScoringInput) -> str:
    input_payload = {
        "id": scoring_input.id,
        "user": scoring_input.user,
        "comment": scoring_input.comment,
        "feature_type": scoring_input.feature_type,
        "feature": scoring_input.feature,
        "impact": scoring_input.impact,
        "urgency": scoring_input.urgency,
    }
    return json.dumps(
        {
            "input": input_payload,
            "impact_criteria": IMPACT_CRITERIA,
            "urgency_criteria": URGENCY_CRITERIA,
        },
        indent=2,
    )


def _parse_dataset_item(item: dict[str, Any]) -> ScoringInput:
    input_payload = item.get("input", item)
    return ScoringInput(
        id=int(item["id"]),
        user=str(input_payload["user"]),
        comment=str(input_payload["comment"]),
        feature_type=str(input_payload["feature_type"]),
        feature=str(input_payload["feature"]),
        impact=_parse_evaluation_score(input_payload["impact"]),
        urgency=_parse_evaluation_score(input_payload["urgency"]),
    )


def _calculate_feature_priority_score(scoring_input: ScoringInput) -> float:
    return round(
        FEATURE_PRIORITY_IMPACT_WEIGHT * int(scoring_input.impact)
        + FEATURE_PRIORITY_URGENCY_WEIGHT * int(scoring_input.urgency),
        1,
    )


def _parse_evaluation_score(value: Any) -> EvaluationScore:
    score = str(value)
    if score not in {"1", "2", "3", "4", "5"}:
        raise ValueError(f"Invalid evaluation score: {value}.")

    return cast(EvaluationScore, score)
