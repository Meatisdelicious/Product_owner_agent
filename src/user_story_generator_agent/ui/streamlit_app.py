from __future__ import annotations
from dataclasses import asdict
import html
from pathlib import Path
import sys
import streamlit as st


# command to start the streamlit app : 
# uv run streamlit run src/user_story_generator_agent/ui/streamlit_app.py --server.headless true --server.port 8501
# uv run streamlit run src/user_story_generator_agent/ui/streamlit_app.py


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SRC_PATH = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_PATH))

from user_story_generator_agent.services.orchestrator import (  # noqa: E402
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
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 1.75rem;
        }

        h1 {
            font-size: 2.6rem !important;
            text-align: center;
            margin-top: 0.25rem;
        }

        h3 {
            font-size: 0.962rem !important;
            margin: 0.479rem 0 0.285rem 0 !important;
        }

        label,
        p,
        li,
        div[data-testid="stMarkdownContainer"] {
            font-size: 0.962rem;
        }

        div[data-testid="stMetricLabel"] p {
            font-size: 0.724rem !important;
            margin-bottom: 0.097rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 0.962rem !important;
        }

        div[data-testid="stMetric"] {
            margin-bottom: 0.241rem;
        }

        div[data-testid="stVerticalBlock"] {
            gap: 0.338rem;
        }

        div[data-testid="stTable"] table {
            font-size: 0.77rem;
        }

        div[data-testid="stTable"] th,
        div[data-testid="stTable"] td {
            padding: 0.241rem 0.482rem !important;
            line-height: 1.155;
        }

        details[data-testid="stExpander"] {
            margin-top: 0.241rem;
        }

        details[data-testid="stExpander"] summary {
            padding: 0.338rem 0.482rem;
        }

        textarea {
            font-size: 0.962rem !important;
        }

        div[data-testid="stButton"] button {
            font-size: 0.962rem;
            padding: 0.482rem 0.962rem;
        }

        div[data-testid="stSpinner"] {
            justify-content: center;
        }

        .user-story-highlight {
            background-color: #fff7cc;
            border-left: 4px solid #f4c430;
            border-radius: 6px;
            font-size: 0.867rem;
            line-height: 1.3;
            padding: 0.482rem 0.722rem;
            margin-bottom: 0.385rem;
        }

        .acceptance-criteria {
            margin-top: 0;
            padding-left: 1.203rem;
            font-size: 0.867rem;
            line-height: 1.251;
        }

        .acceptance-criteria li {
            margin-bottom: 0.097rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Product Owner Agent")

    _, input_col, _ = st.columns([1, 2, 1])
    with input_col:
        comment = st.text_area(
            "User feedback comment",
            value=EXAMPLE_COMMENT,
            height=94,
        )
        analyze = st.button("Generate Analysis", type="primary")
        spinner_placeholder = st.empty()
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
        with spinner_placeholder:
            with st.spinner("Running the full pipeline..."):
                result = _get_agent().analyze(feedback)
    except Exception as exc:  # pragma: no cover - Streamlit-facing error handling
        st.error("The pipeline could not complete.")
        st.exception(exc)
        st.stop()

    output = asdict(result)
    _render_output(output)


def _render_output(output: dict[str, object]) -> None:
    st.markdown("<h3><u>Feature Analysis</u></h3>", unsafe_allow_html=True)
    feature_col, type_col = st.columns(2)
    feature_col.markdown(f"**Feature :** {html.escape(str(output['feature']))}")
    type_col.markdown(f"**Feature type :** {html.escape(str(output['feature_type']))}")

    priority_col, complexity_col = st.columns(2)
    with priority_col:
        st.markdown("<h3><u>Prioritization</u></h3>", unsafe_allow_html=True)
        priority_table_col, _ = st.columns([0.65, 0.35])
        with priority_table_col:
            st.markdown(
                "**MoSCoW result :** "
                f"{html.escape(str(output['moscow_category_result']))}"
            )
            st.table(
                [
                    {"Metric": "Impact", "Value": str(output["impact"])},
                    {"Metric": "Urgency", "Value": str(output["urgency"])},
                    {
                        "Metric": "Priority score",
                        "Value": str(output["feature_priority_score"]),
                    },
                ]
            )
            with st.expander("View justifications"):
                st.markdown("<u>Impact justification</u>", unsafe_allow_html=True)
                st.write(str(output["impact_justification"]))

                st.markdown("<u>Urgency justification</u>", unsafe_allow_html=True)
                st.write(str(output["urgency_justification"]))

                st.markdown("<u>Recommendation</u>", unsafe_allow_html=True)
                st.write(str(output["feature_recommendation_justification"]))

    with complexity_col:
        st.markdown("<h3><u>Complexity</u></h3>", unsafe_allow_html=True)
        complexity_table_col, _ = st.columns([0.65, 0.35])
        with complexity_table_col:
            st.markdown(
                "**Development complexity :** "
                f"{html.escape(str(output['development_complexity_estimation']))}"
            )
            complexity = output["complexity_factors"]
            if isinstance(complexity, dict):
                st.table(
                    [
                        {
                            "Metric": "Backend",
                            "Value": str(complexity["backend_changes"]),
                        },
                        {
                            "Metric": "Frontend",
                            "Value": str(complexity["frontend_changes"]),
                        },
                        {
                            "Metric": "Data model",
                            "Value": str(complexity["data_model_changes"]),
                        },
                        {
                            "Metric": "Security",
                            "Value": str(complexity["security_constraints"]),
                        },
                        {
                            "Metric": "Integration",
                            "Value": str(complexity["integration_dependencies"]),
                        },
                    ]
                )

    st.markdown("<h3><u>User Story</u></h3>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="user-story-highlight">
            {html.escape(str(output["user_story"]))}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<h3><u>Acceptance Criteria</u></h3>", unsafe_allow_html=True)
    criteria_items = "\n".join(
        f"<li>{html.escape(str(criterion))}</li>"
        for criterion in output["feature_acceptance_criteria"]
    )
    st.markdown(
        f'<ul class="acceptance-criteria">{criteria_items}</ul>',
        unsafe_allow_html=True,
    )

    with st.expander("Raw JSON output"):
        st.json(output)


if __name__ == "__main__":
    main()
