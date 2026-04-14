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
- development_complexity_estimation (input_context : feature, feature_type, feature_recommendation_justification, complexity_factors)


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
},