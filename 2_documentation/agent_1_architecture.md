# Agent 1 Architecture

Agent 1 extracts a product feature from a user comment.

It receives:
- `id`
- `user`
- `comment`

It returns:
- `feature_type`
- `feature`

```mermaid
flowchart TD
    A["agent_1_dataset.json"] --> B["get_dataset_item(comment_id, dataset_path)"]
    B --> C["_parse_dataset_item(item)"]
    C --> D["ExtractorInput<br/>id, user, comment"]

    D --> E["extract_feature_from_dataset(...)"]
    E --> F["FeatureExtractor"]
    F --> G["extract(comment)"]

    G --> H["EXTRACTOR_PROMPT<br/>ChatPromptTemplate"]
    H --> I["System prompt<br/>Product feature extractor"]
    H --> J["User prompt<br/>Comment: {comment}"]

    I --> K["LangChain chain"]
    J --> K
    K --> L["ChatOpenAI<br/>MODEL_ID + OPENAI_API_KEY"]
    L --> M["with_structured_output(_ExtractorSchema)"]

    M --> N["_ExtractorSchema<br/>feature_type, feature"]
    N --> O["ExtractorOutput"]
    O --> P["JSON result"]
```

## Runtime Flow

```mermaid
sequenceDiagram
    participant Test as tests/run_extractor.py
    participant Dataset as agent_1_dataset.json
    participant Service as extractor.py
    participant Prompt as ChatPromptTemplate
    participant LLM as ChatOpenAI
    participant Schema as _ExtractorSchema

    Test->>Service: get_dataset_item(comment_id, dataset_path)
    Service->>Dataset: Load JSON records
    Dataset-->>Service: Raw dataset item
    Service-->>Test: ExtractorInput

    Test->>Service: extract_feature_from_dataset(comment_id, dataset_path)
    Service->>Dataset: Load matching comment
    Service->>Prompt: Build system and user messages
    Prompt->>LLM: Invoke chain with comment
    LLM->>Schema: Return structured output
    Schema-->>Service: feature_type and feature
    Service-->>Test: ExtractorOutput
```

## Main Components

| Component | Role |
| --- | --- |
| `ExtractorInput` | Internal input object containing `id`, `user`, and `comment`. |
| `ExtractorOutput` | Internal output object containing `feature_type` and `feature`. |
| `_ExtractorSchema` | Pydantic schema used by LangChain structured output. |
| `EXTRACTOR_PROMPT` | LangChain prompt containing the system instruction and comment input. |
| `FeatureExtractor` | Service class that builds the chain and invokes the LLM. |
| `ChatOpenAI` | LangChain OpenAI wrapper using `OPENAI_API_KEY` and `MODEL_ID`. |

