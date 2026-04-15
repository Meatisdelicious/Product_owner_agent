# Product_owner_agent

Data input : 
{
  "id": 1,
  "user": "Marie_Dupont",
  "comment": "We need role-based permissions because managing access across large teams is risky right now. Admin control is not granular enough.",
},

1) content extraction : 
Data extraction after input : 
{
  "feature_type": "feature_request",
  "feature": "role-based permissions",
},

2) Scoring : 

  - feature scoring : 
      - impact = 1 to 5 
        - "impact_criteria": {
                                "5": "Security risk or blocking core functionality",
                                "4": "Major workflow impact",
                                "3": "Moderate inefficiency",
                                "2": "Minor inconvenience",
                                "1": "Negligible"
                              }
      - urgency = 1 to 5
        - "urgency_criteria": {
                                "5": "Immediate issue causing active risk or blocking users",
                                "4": "Frequent problem needing near-term action",
                                "3": "Recurring issue, but manageable in the short term",
                                "2": "Occasional issue with workaround available",
                                "1": "Low time sensitivity"
                              }
      - write impact justification
      - write urgency justification
  - prioritization framework (moscow): 
      - feature_priority_score = 0.4 * impact + 0.6 * urgency
      - MoSCoW_category_result =  4.5-5.0   = Must have
                                  3.5-4.49  = Should have
                                  2.5-3.49  = Could have
                                  below 2.5 = Won’t have for now
      - feature_recommendation_justification = comment+impact+urgency+feature_priority_score+MoSCoW_category_result
        - template : This feature should be prioritized as a [MoSCoW_category_result] because it [impact_justification]. 
                      The issue is [urgency_justification], as indicated by [comment].

After processing 
{
  "feature_type": "feature_request",
  "feature": "role-based permissions",
  "impact": "5",
  "urgency": "5",
  "impact_justification":"Affects core access control across large teams, with strong implications for security and scalability.",
  "urgency_justification": "Represents an immediate risk in current operations, potentially leading to access control issues or misuse.",
  "feature_priority_score": "5",
  "MoSCoW_category_result": "Must have",
  "feature_recommendation_justification": "This feature should be prioritized as a Must have because it directly affects access control, security, and safe administration across large teams. The comment indicates an active operational risk, not just a convenience improvement."
},


1) Story writing : 
   - user story generation :
       -  formated strucuture  : As a [user type], I want [feature], so that [impact+urgency].
       -  based on the user_comment, feature_type and feature_request
   - development_complexity_estimation (according to all the data): (low,medium,high)
       - "complexity_factors": {
                                "backend_changes": 1,
                                "frontend_changes": 1,
                                "data_model_changes": 1,
                                "security_constraints": 1,
                                "integration_dependencies": 1
                                }
       -  development_complexity_estimation = sum(complexity factors)
             -  Low    = 1-2 factors
                Medium = 3-4
                High   = 5+
       - feature_acceptance_criteria : 
           - Generate 3 feature_acceptance_criteria per user_comment
                  template : 
                      Core functionality (does the feature actually work)
                      Correct behavior / constraint (permissions, sync consistency, relevance)
                      Real-world usage condition (updates, failures, large scale)

Expected final data output : 
{
  "feature_type": "feature_request",
  "feature": "role-based permissions",
  "impact": "5",
  "urgency": "5",
  "impact_justification":"Affects core access control across large teams, with strong implications for security and scalability.",
  "urgency_justification": "Represents an immediate risk in current operations, potentially leading to access control issues or misuse.",
  "feature_priority_score": "5",
  "MoSCoW_category_result": "Must have",
  "feature_recommendation_justification": "This feature should be prioritized as a Must have because it directly affects access control, security, and safe administration across large teams. The comment indicates an active operational risk, not just a convenience improvement.",
  "user_story": "As an admin, I want to define granular roles and permissions so that users only access what they are allowed to.",
  "complexity_factors": {
                          "backend_changes": 1,
                          "frontend_changes": 1,
                          "data_model_changes": 1,
                          "security_constraints": 1,
                          "integration_dependencies": 1
                        },
  "development_complexity_estimation": "High",
  "feature_acceptance_criteria": [
                                  "A user can be assigned a role with specific permission levels.",
                                  "The system restricts access to actions based on the user's assigned role.",
                                  "The system updates user permissions immediately after a role change."
                                  ]
},



Tech stack : 

AI/ML:
- LangChain - Framework for building applications with LLMs
- LangGraph - Library for building stateful, multi-actor applications with LLMs
- OpenAI API 

Package Management: 
- uv 





acceptance_criteria template : 

Generate exactly 3 acceptance criteria for the feature.

Structure:
1. Core functionality → what the user must be able to do
2. Constraint or validation → what the system must enforce or guarantee
3. Real-world condition → behavior under update, scale, or failure

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

