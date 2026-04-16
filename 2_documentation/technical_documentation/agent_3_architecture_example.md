Agent 3: Story Writer

Input: 
- id
- user
- comment
- feature
- feature_type
- impact 
- urgency 
- feature_recommendation_justification

Output : 
- user story                        (input_context : feature+impact+urgency+template)
- complexity_factors                (input_context: comment + feature + feature_type + impact + urgency + feature_recommendation_justification + complexity_factor_criteria)
- development_complexity_estimation (input_context : feature, feature_type, feature_recommendation_justification, complexity_factors)
- feature_acceptance_criteria (input_context : comment+feature+feature_type + user_story + template)

input_example : 
{
  "id": 1,
  "user": "Marie_Dupont",
  "comment": "We need role-based permissions because managing access across large teams is risky right now. Admin control is not granular enough.",
  "feature_type": "feature_request",
  "feature": "role-based permissions",
  "impact": 5,
  "urgency": 4
},

output_example : 
{
  "user_story": "As an admin, I want to define granular roles and permissions so that users only access what they are allowed to.",
  "complexity_factors": {
        "backend_changes": 1,
        "frontend_changes": 1,
        "data_model_changes": 1,
        "security_constraints": 1,
        "integration_dependencies": 0
      },
      "development_complexity_estimation": "Medium",
      "feature_acceptance_criteria": [
        "An admin can create and assign roles with distinct permission levels.",
        "A user can only access actions and data permitted by their assigned role.",
        "When a user's role is updated, the new permissions apply immediately."
      ]
},