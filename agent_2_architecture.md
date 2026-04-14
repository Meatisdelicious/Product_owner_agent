Agent 2.1: evaluation

Input: 
- id
- user
- comment
- feature_type
- feature

output : 
- impact                               (input_context : comment + feature_type + feature + impact_criteria) 
- urgency                              (input_context : comment + feature_type + feature + urgency_criteria) 

input_example : 
{
  "id": 1,
  "user": "Marie_Dupont",
  "comment": "We need role-based permissions because managing access across large teams is risky right now. Admin control is not granular enough.",
  "feature_type": "feature_request",
  "feature": "role-based permissions",
},

output_example : 
{
  "impact": "5",
  "urgency": "5",
},

Agent 2.2: scoring

input: 
- comment 
- feature_type
- feature 
- impact
- urgency
 
output: 
- impact_justifications                (input_context : comment + feature_type + feature + impact_criteria, impact)
- urgency_justifications               (input_context : comment + feature_type + feature + urgency_criteria, urgency)
- feature_priority_score               (input_context : impact + urgency)
- moscow_category_result               (input_context : feature_priority_score) 
- feature_recommendation_justification (input_context : comment+impact+urgency+feature_priority_score+MoSCoW_category_result)

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
  "impact_justification":"Affects core access control across large teams, with strong implications for security and scalability.",
  "urgency_justification": "Represents an immediate risk in current operations, potentially leading to access control issues or misuse.",
},