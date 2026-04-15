from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from user_story_generator_agent.services.evaluation import (
    EvaluationInput,
    EvaluationOutput,
    FeatureEvaluator,
)
from user_story_generator_agent.services.extractor import (
    DEFAULT_DATASET_PATH as DEFAULT_FEEDBACK_DATASET_PATH,
)
from user_story_generator_agent.services.extractor import (
    ExtractorOutput,
    FeatureExtractor,
    get_dataset_item,
)
from user_story_generator_agent.services.scoring import (
    FeatureScorer,
    MoscowCategory,
    ScoringInput,
    ScoringOutput,
)
from user_story_generator_agent.services.user_story import (
    ComplexityFactors,
    DevelopmentComplexity,
    UserStoryInput,
    UserStoryOutput,
    UserStoryWriter,
)


@dataclass(frozen=True)
class FeedbackInput:
    id: int
    user: str
    comment: str


@dataclass(frozen=True)
class ProductOwnerOutput:
    feature_type: str
    feature: str
    impact: str
    urgency: str
    impact_justification: str
    urgency_justification: str
    feature_priority_score: float
    moscow_category_result: MoscowCategory
    feature_recommendation_justification: str
    user_story: str
    complexity_factors: ComplexityFactors
    development_complexity_estimation: DevelopmentComplexity
    feature_acceptance_criteria: list[str]


class ProductOwnerAgent:
    def __init__(
        self,
        extractor: FeatureExtractor | None = None,
        evaluator: FeatureEvaluator | None = None,
        scorer: FeatureScorer | None = None,
        writer: UserStoryWriter | None = None,
    ) -> None:
        self.extractor = extractor or FeatureExtractor()
        self.evaluator = evaluator or FeatureEvaluator()
        self.scorer = scorer or FeatureScorer()
        self.writer = writer or UserStoryWriter()

    def analyze(self, feedback: FeedbackInput) -> ProductOwnerOutput:
        extraction = self.extractor.extract(feedback.comment)
        evaluation = self._evaluate_feature(feedback, extraction)
        scoring = self._score_feature(feedback, extraction, evaluation)
        story = self._write_user_story(feedback, extraction, evaluation, scoring)

        return ProductOwnerOutput(
            feature_type=extraction.feature_type,
            feature=extraction.feature,
            impact=evaluation.impact,
            urgency=evaluation.urgency,
            impact_justification=scoring.impact_justification,
            urgency_justification=scoring.urgency_justification,
            feature_priority_score=scoring.feature_priority_score,
            moscow_category_result=scoring.moscow_category_result,
            feature_recommendation_justification=(
                scoring.feature_recommendation_justification
            ),
            user_story=story.user_story,
            complexity_factors=story.complexity_factors,
            development_complexity_estimation=(
                story.development_complexity_estimation
            ),
            feature_acceptance_criteria=story.feature_acceptance_criteria,
        )

    def _evaluate_feature(
        self,
        feedback: FeedbackInput,
        extraction: ExtractorOutput,
    ) -> EvaluationOutput:
        return self.evaluator.evaluate(
            EvaluationInput(
                id=feedback.id,
                user=feedback.user,
                comment=feedback.comment,
                feature_type=extraction.feature_type,
                feature=extraction.feature,
            )
        )

    def _score_feature(
        self,
        feedback: FeedbackInput,
        extraction: ExtractorOutput,
        evaluation: EvaluationOutput,
    ) -> ScoringOutput:
        return self.scorer.score(
            ScoringInput(
                id=feedback.id,
                user=feedback.user,
                comment=feedback.comment,
                feature_type=extraction.feature_type,
                feature=extraction.feature,
                impact=evaluation.impact,
                urgency=evaluation.urgency,
            )
        )

    def _write_user_story(
        self,
        feedback: FeedbackInput,
        extraction: ExtractorOutput,
        evaluation: EvaluationOutput,
        scoring: ScoringOutput,
    ) -> UserStoryOutput:
        return self.writer.write(
            UserStoryInput(
                id=feedback.id,
                user=feedback.user,
                comment=feedback.comment,
                feature=extraction.feature,
                feature_type=extraction.feature_type,
                impact=evaluation.impact,
                urgency=evaluation.urgency,
                feature_recommendation_justification=(
                    scoring.feature_recommendation_justification
                ),
            )
        )


def analyze_feedback(
    feedback: FeedbackInput,
    agent: ProductOwnerAgent | None = None,
) -> ProductOwnerOutput:
    product_owner_agent = agent or ProductOwnerAgent()
    return product_owner_agent.analyze(feedback)


def analyze_feedback_from_dataset(
    comment_id: int,
    dataset_path: Path | str = DEFAULT_FEEDBACK_DATASET_PATH,
    agent: ProductOwnerAgent | None = None,
) -> ProductOwnerOutput:
    dataset_item = get_dataset_item(comment_id, dataset_path)
    return analyze_feedback(
        FeedbackInput(
            id=dataset_item.id,
            user=dataset_item.user,
            comment=dataset_item.comment,
        ),
        agent=agent,
    )


def build_feedback_input(payload: dict[str, Any]) -> FeedbackInput:
    return FeedbackInput(
        id=int(payload["id"]),
        user=str(payload["user"]),
        comment=str(payload["comment"]),
    )

