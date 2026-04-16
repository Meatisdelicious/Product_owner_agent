from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.orchestrator import (
    FeedbackInput,
    ProductOwnerAgent,
)


EXAMPLE_COMMENT = (
    "We need role-based permissions because managing access across large teams "
    "is risky right now. Admin control is not granular enough."
)


@st.cache_resource
def _get_agent() -> ProductOwnerAgent:
    return ProductOwnerAgent()


def main() -> None:
    st.set_page_config(
        page_title="Product Owner Agent",
        layout="wide",
    )

    st.title("Product Owner Agent")
    st.caption("Browser -> Streamlit server -> ProductOwnerAgent -> OpenAI API")

    comment = st.text_area(
        "User feedback comment",
        value=EXAMPLE_COMMENT,
        height=150,
    )

    analyze = st.button("Run full pipeline", type="primary")
    if not analyze:
        st.stop()

    if not comment.strip():
        st.error("Enter a user feedback comment before running the pipeline.")
        st.stop()

    feedback = FeedbackInput(
        id=1,
        user="manual_input",
        comment=comment.strip(),
    )

    try:
        with st.spinner("Running the full pipeline..."):
            result = _get_agent().analyze(feedback)
    except Exception as exc:  # pragma: no cover - Streamlit-facing error handling
        st.error("The pipeline could not complete.")
        st.exception(exc)
        st.stop()

    output = asdict(result)
    _render_output(output)


def _render_output(output: dict[str, object]) -> None:
    st.subheader("Feature Analysis")
    feature_col, type_col = st.columns(2)
    feature_col.metric("Feature", str(output["feature"]))
    type_col.metric("Feature type", str(output["feature_type"]))

    st.subheader("Prioritization")
    impact_col, urgency_col, score_col, moscow_col = st.columns(4)
    impact_col.metric("Impact", str(output["impact"]))
    urgency_col.metric("Urgency", str(output["urgency"]))
    score_col.metric("Priority score", str(output["feature_priority_score"]))
    moscow_col.metric("MoSCoW", str(output["moscow_category_result"]))

    st.write("Impact justification")
    st.info(str(output["impact_justification"]))

    st.write("Urgency justification")
    st.info(str(output["urgency_justification"]))

    st.write("Recommendation")
    st.success(str(output["feature_recommendation_justification"]))

    st.subheader("User Story")
    st.write(str(output["user_story"]))

    st.subheader("Acceptance Criteria")
    for criterion in output["feature_acceptance_criteria"]:
        st.write(f"- {criterion}")

    st.subheader("Complexity")
    complexity = output["complexity_factors"]
    if isinstance(complexity, dict):
        backend_col, frontend_col, data_col, security_col, integration_col = st.columns(5)
        backend_col.metric("Backend", str(complexity["backend_changes"]))
        frontend_col.metric("Frontend", str(complexity["frontend_changes"]))
        data_col.metric("Data model", str(complexity["data_model_changes"]))
        security_col.metric("Security", str(complexity["security_constraints"]))
        integration_col.metric(
            "Integration",
            str(complexity["integration_dependencies"]),
        )

    st.metric(
        "Development complexity",
        str(output["development_complexity_estimation"]),
    )

    with st.expander("Raw JSON output"):
        st.json(output)


if __name__ == "__main__":
    main()
