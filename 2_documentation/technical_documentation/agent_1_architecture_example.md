Agent 1: Extractor

Input: 
- id
- user
- comment

output : 
- feature_type                        
- feature

input_example : 
{
  "id": 1,
  "user": "Marie_Dupont",
  "comment": "We need role-based permissions because managing access across large teams is risky right now. Admin control is not granular enough.",
},

output_example : 
{
  "feature_type": "feature_request",
  "feature": "role-based permissions",
},