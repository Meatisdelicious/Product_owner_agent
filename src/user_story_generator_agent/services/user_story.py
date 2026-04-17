from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal, cast

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from user_story_generator_agent.context.criterias import COMPLEXITY_FACTOR_CRITERIA


EvaluationScore = Literal["1", "2", "3", "4", "5"]
ComplexityFlag = Literal[0, 1]
DevelopmentComplexity = Literal["Low", "Medium", "High"]

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_DATASET_PATH = PROJECT_ROOT / "1_Data" / "agent_3_datset.json"
USER_STORY_TEMPLATE = (
    "As a [user type], I want [feature], so that [impact and urgency outcome]."
)
ACCEPTANCE_CRITERIA_TEMPLATE = """
Generate exactly 3 acceptance criteria for the feature.

Structure:
1. Core functionality -> what the user must be able to do
2. Constraint or validation -> what the system must enforce or guarantee
3. Real-world condition -> behavior under update, scale, or failure

Rules:
- Each criterion must be specific, testable, and based on the user comment.
- Avoid vague statements like "the feature should work properly".
- Focus on observable system behavior.
- Each criterion must be one sentence.
- Do not include implementation details (no tech, no architecture).
- Return the result as a JSON array of strings.

Additional constraints:
- Each sentence must start with "A user can" or "The system".
- Maximum 20 words per criterion.
- No duplicated meaning across criteria.
"""

USER_STORY_SYSTEM_PROMPT = """
You are Agent 3, a product user story writer.

Write one user story for the extracted product feature.
Generate exactly 3 acceptance criteria for the feature.

Use this template:
As a [user type], I want [feature], so that [impact and urgency outcome].

Return only JSON with:
- user_story: one concise user story following the template
- complexity_factors: object with backend_changes, frontend_changes,
  data_model_changes, security_constraints, and integration_dependencies,
  each as 0 or 1
- feature_acceptance_criteria: JSON array of exactly 3 strings

Use the feature, impact, urgency, and feature_recommendation_justification as context.
Do not calculate development_complexity_estimation.
Do not add prioritization scores or explanations.
"""


@dataclass(frozen=True)
class UserStoryInput:
    """Prioritized feature context passed to the user story writer."""

    id: int
    user: str
    comment: str
    feature: str
    feature_type: str
    impact: EvaluationScore
    urgency: EvaluationScore
    feature_recommendation_justification: str


@dataclass(frozen=True)
class UserStoryOutput:
    """User story, acceptance criteria, and complexity estimate from Agent 3."""

    user_story: str
    complexity_factors: ComplexityFactors
    development_complexity_estimation: DevelopmentComplexity
    feature_acceptance_criteria: list[str]


@dataclass(frozen=True)
class ComplexityFactors:
    """Binary indicators used to estimate development complexity."""

    backend_changes: ComplexityFlag
    frontend_changes: ComplexityFlag
    data_model_changes: ComplexityFlag
    security_constraints: ComplexityFlag
    integration_dependencies: ComplexityFlag


class _ComplexityFactorsSchema(BaseModel):
    backend_changes: ComplexityFlag = Field(
        description=(
            "1 if backend, API, or business logic changes are likely needed, "
            "otherwise 0."
        )
    )
    frontend_changes: ComplexityFlag = Field(
        description="1 if user interface changes are likely needed, otherwise 0."
    )
    data_model_changes: ComplexityFlag = Field(
        description=(
            "1 if database, schema, or domain model changes are likely needed, "
            "otherwise 0."
        )
    )
    security_constraints: ComplexityFlag = Field(
        description=(
            "1 if permissions, access control, privacy, or security constraints are "
            "involved, otherwise 0."
        )
    )
    integration_dependencies: ComplexityFlag = Field(
        description=(
            "1 if external systems, APIs, or third-party integrations are involved, "
            "otherwise 0."
        )
    )


class _UserStorySchema(BaseModel):
    user_story: str = Field(
        description="One concise user story following the requested template."
    )
    complexity_factors: _ComplexityFactorsSchema
    feature_acceptance_criteria: list[str] = Field(
        min_length=3,
        max_length=3,
        description=(
            "Exactly 3 acceptance criteria, each specific, testable, one sentence, "
            "20 words maximum, and starting with 'A user can' or 'The system'."
        ),
    )


USER_STORY_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", USER_STORY_SYSTEM_PROMPT),
        ("user", "{payload}"),
    ]
)


class UserStoryWriter:
    """Generate user stories, acceptance criteria, and complexity factors."""

    def __init__(self, llm: Any | None = None) -> None:
        self.llm = llm or self._build_default_llm()
        self.chain = USER_STORY_PROMPT | self.llm.with_structured_output(
            _UserStorySchema
        )

    def write(self, user_story_input: UserStoryInput) -> UserStoryOutput:
        """Write one user story output from prioritized feature context."""
        payload = self.chain.invoke(
            {"payload": _build_user_story_prompt(user_story_input)}
        )
        complexity_factors = ComplexityFactors(
            backend_changes=payload.complexity_factors.backend_changes,
            frontend_changes=payload.complexity_factors.frontend_changes,
            data_model_changes=payload.complexity_factors.data_model_changes,
            security_constraints=payload.complexity_factors.security_constraints,
            integration_dependencies=(
                payload.complexity_factors.integration_dependencies
            ),
        )
        return UserStoryOutput(
            user_story=payload.user_story,
            complexity_factors=complexity_factors,
            development_complexity_estimation=(
                _calculate_development_complexity_estimation(complexity_factors)
            ),
            feature_acceptance_criteria=list(payload.feature_acceptance_criteria),
        )

    def write_from_dataset(
        self,
        comment_id: int,
        dataset_path: Path | str = DEFAULT_DATASET_PATH,
    ) -> UserStoryOutput:
        """Write a user story from one item in a user story dataset."""
        dataset_item = get_user_story_dataset_item(comment_id, dataset_path)
        return self.write(dataset_item)

    def _build_default_llm(self) -> Any:
        """Build the default OpenAI chat model from environment variables."""
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
                "The langchain-openai package is required. "
                "Install dependencies with `uv sync`."
            ) from exc

        return ChatOpenAI(
            temperature=0.2,
            openai_api_key=os.environ["OPENAI_API_KEY"],
            model=os.environ["MODEL_ID"],
        )


def load_user_story_dataset(
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> list[UserStoryInput]:
    """Load user story input items from a JSON dataset."""
    path = Path(dataset_path)
    with path.open(encoding="utf-8") as dataset_file:
        raw_items = json.load(dataset_file)

    return [_parse_dataset_item(item) for item in raw_items]


def get_user_story_dataset_item(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
) -> UserStoryInput:
    """Return one user story dataset item by comment id."""
    for item in load_user_story_dataset(dataset_path):
        if item.id == comment_id:
            return item

    raise ValueError(f"No comment found with id {comment_id}.")


def write_user_story_from_dataset(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_DATASET_PATH,
    llm: Any | None = None,
) -> UserStoryOutput:
    """Convenience wrapper for writing one dataset item."""
    writer = UserStoryWriter(llm=llm)
    return writer.write_from_dataset(comment_id, dataset_path)


def _build_user_story_prompt(user_story_input: UserStoryInput) -> str:
    """Build the JSON payload sent to the user story prompt."""
    input_payload = {
        "id": user_story_input.id,
        "user": user_story_input.user,
        "comment": user_story_input.comment,
        "feature": user_story_input.feature,
        "feature_type": user_story_input.feature_type,
        "impact": user_story_input.impact,
        "urgency": user_story_input.urgency,
        "feature_recommendation_justification": (
            user_story_input.feature_recommendation_justification
        ),
    }
    return json.dumps(
        {
            "input": input_payload,
            "user_story_template": USER_STORY_TEMPLATE,
            "acceptance_criteria_template": ACCEPTANCE_CRITERIA_TEMPLATE,
            "complexity_factor_criteria": COMPLEXITY_FACTOR_CRITERIA,
        },
        indent=2,
    )


def _parse_dataset_item(item: dict[str, Any]) -> UserStoryInput:
    """Convert a raw dataset row into a user story input."""
    input_payload = item.get("input", item)
    return UserStoryInput(
        id=int(item["id"]),
        user=str(input_payload["user"]),
        comment=str(input_payload["comment"]),
        feature=str(input_payload["feature"]),
        feature_type=str(input_payload["feature_type"]),
        impact=_parse_evaluation_score(input_payload["impact"]),
        urgency=_parse_evaluation_score(input_payload["urgency"]),
        feature_recommendation_justification=str(
            input_payload["feature_recommendation_justification"]
        ),
    )


def _parse_evaluation_score(value: Any) -> EvaluationScore:
    """Validate and cast a raw value to an evaluation score literal."""
    score = str(value)
    if score not in {"1", "2", "3", "4", "5"}:
        raise ValueError(f"Invalid evaluation score: {value}.")

    return cast(EvaluationScore, score)


def _calculate_development_complexity_estimation(
    complexity_factors: ComplexityFactors,
) -> DevelopmentComplexity:
    """Estimate development complexity from enabled complexity factors."""
    factor_count = (
        complexity_factors.backend_changes
        + complexity_factors.frontend_changes
        + complexity_factors.data_model_changes
        + complexity_factors.security_constraints
        + complexity_factors.integration_dependencies
    )

    if factor_count <= 2:
        return "Low"
    if factor_count <= 4:
        return "Medium"

    return "High"
