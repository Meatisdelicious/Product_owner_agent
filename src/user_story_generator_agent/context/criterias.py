IMPACT_CRITERIA = {
    "5": "Security risk or blocking core functionality",
    "4": "Major workflow impact",
    "3": "Moderate inefficiency",
    "2": "Minor inconvenience",
    "1": "Negligible",
}

URGENCY_CRITERIA = {
    "5": "Immediate issue causing active risk or blocking users",
    "4": "Frequent problem needing near-term action",
    "3": "Recurring issue, but manageable in the short term",
    "2": "Occasional issue with workaround available",
    "1": "Low time sensitivity",
}

COMPLEXITY_FACTOR_CRITERIA = {
    "backend_changes": (
        "1 if backend, API, or business logic changes are likely needed, otherwise 0"
    ),
    "frontend_changes": "1 if user interface changes are likely needed, otherwise 0",
    "data_model_changes": (
        "1 if database, schema, or domain model changes are likely needed, otherwise 0"
    ),
    "security_constraints": (
        "1 if permissions, access control, privacy, or security constraints are "
        "involved, otherwise 0"
    ),
    "integration_dependencies": (
        "1 if external systems, APIs, or third-party integrations are involved, "
        "otherwise 0"
    ),
}
