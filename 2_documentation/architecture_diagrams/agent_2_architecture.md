# Agent 2 Architecture (evaluation + scoring)

Agent 2 evaluates and prioritizes an extracted product feature.

It is split into two services:
- Agent 2.1 evaluates `impact` and `urgency`.
- Agent 2.2 computes prioritization values and generates justifications.

## Inputs

Agent 2.1 receives:
- `id`
- `user`
- `comment`
- `feature_type`
- `feature`

Agent 2.2 receives:
- `id`
- `user`
- `comment`
- `feature_type`
- `feature`
- `impact`
- `urgency`

## Outputs

Agent 2.1 returns:
- `impact`
- `urgency`

Agent 2.2 returns:
- `impact_justification`
- `urgency_justification`
- `feature_priority_score`
- `moscow_category_result`
- `feature_recommendation_justification`

```mermaid
flowchart TD
    A["agent_2.1_dataset.json"] --> B["get_evaluation_dataset_item(comment_id, dataset_path)"]
    B --> C["_parse_dataset_item(item)"]
    C --> D["EvaluationInput<br/>id, user, comment, feature_type, feature"]

    D --> E["FeatureEvaluator"]
    E --> F["EVALUATION_PROMPT<br/>ChatPromptTemplate"]
    F --> G["impact_criteria + urgency_criteria"]
    F --> H["ChatOpenAI"]
    G --> I["LangChain chain"]
    H --> I
    I --> J["with_structured_output(_EvaluationSchema)"]
    J --> K["EvaluationOutput<br/>impact, urgency"]

    K --> L["agent_2.2_dataset.json<br/>or downstream scoring input"]
    L --> M["get_scoring_dataset_item(comment_id, dataset_path)"]
    M --> N["ScoringInput<br/>id, user, comment, feature_type, feature, impact, urgency"]

    N --> O["FeatureScorer"]
    O --> P["_calculate_feature_priority_score<br/>0.4 impact + 0.6 urgency"]
    P --> Q["_calculate_moscow_category_result"]
    Q --> R["SCORING_PROMPT<br/>ChatPromptTemplate"]
    R --> S["impact_criteria + urgency_criteria"]
    R --> T["ChatOpenAI"]
    S --> U["LangChain chain"]
    T --> U
    U --> V["with_structured_output(_ScoringSchema)"]
    V --> W["ScoringOutput"]
```

## Agent 2.1 Runtime Flow

```mermaid
sequenceDiagram
    participant Test as tests/run_evaluation.py
    participant Dataset as agent_2.1_dataset.json
    participant Service as evaluation.py
    participant Prompt as EVALUATION_PROMPT
    participant LLM as ChatOpenAI
    participant Schema as _EvaluationSchema

    Test->>Service: get_evaluation_dataset_item(comment_id, dataset_path)
    Service->>Dataset: Load JSON records
    Dataset-->>Service: Raw dataset item
    Service-->>Test: EvaluationInput

    Test->>Service: evaluate_feature_from_dataset(comment_id, dataset_path)
    Service->>Dataset: Load matching feature context
    Service->>Prompt: Build payload with input and scoring criteria
    Prompt->>LLM: Invoke chain
    LLM->>Schema: Return structured output
    Schema-->>Service: impact and urgency
    Service-->>Test: EvaluationOutput
```

## Agent 2.2 Runtime Flow

```mermaid
sequenceDiagram
    participant Test as tests/run_scoring.py
    participant Dataset as agent_2.2_dataset.json
    participant Service as scoring.py
    participant Prompt as SCORING_PROMPT
    participant LLM as ChatOpenAI
    participant Schema as _ScoringSchema

    Test->>Service: get_scoring_dataset_item(comment_id, dataset_path)
    Service->>Dataset: Load JSON records
    Dataset-->>Service: Raw dataset item
    Service-->>Test: ScoringInput

    Test->>Service: score_feature_from_dataset(comment_id, dataset_path)
    Service->>Dataset: Load matching scored feature
    Service->>Service: Calculate feature_priority_score
    Service->>Service: Calculate moscow_category_result
    Service->>Prompt: Build payload with input, scores, category, and criteria
    Prompt->>LLM: Invoke chain
    LLM->>Schema: Return structured justifications
    Schema-->>Service: impact, urgency, and recommendation justifications
    Service-->>Test: ScoringOutput
```

## Main Components

| Component | Role |
| --- | --- |
| `EvaluationInput` | Input object for impact and urgency evaluation. |
| `EvaluationOutput` | Output object containing `impact` and `urgency`. |
| `_EvaluationSchema` | Pydantic schema used by LangChain structured output for Agent 2.1. |
| `EVALUATION_PROMPT` | LangChain prompt containing the evaluation instruction and criteria payload. |
| `FeatureEvaluator` | Service class that evaluates `impact` and `urgency` with the LLM. |
| `ScoringInput` | Input object for prioritization and justification generation. |
| `ScoringOutput` | Output object containing justifications, priority score, and MoSCoW category. |
| `_ScoringSchema` | Pydantic schema used by LangChain structured output for Agent 2.2 justifications. |
| `SCORING_PROMPT` | LangChain prompt containing the scoring justification instruction and criteria payload. |
| `FeatureScorer` | Service class that computes priority values and invokes the LLM for justifications. |
| `ChatOpenAI` | LangChain OpenAI wrapper using `OPENAI_API_KEY` and `MODEL_ID`. |

## Deterministic Rules

Agent 2.2 computes these values locally before calling the LLM:

```text
feature_priority_score = 0.4 * impact + 0.6 * urgency
```

```text
feature_priority_score >= 4.5 -> Must have
feature_priority_score >= 3.5 -> Should have
feature_priority_score >= 2.5 -> Could have
feature_priority_score < 2.5  -> Won't have for now
```

