Agent 1: Extractor
Input: 
- id
- user
- comment

Output:
- feature_type                        
- feature

Agent 2: Prioritizer/scoring
Input:
- id
- user
- comment
- feature_type
- feature

Output 1: 
- impact                               (input_context : comment + feature_type + feature + impact_criteria) 
- urgency                              (input_context : comment + feature_type + feature + urgency_criteria) 

output 2: 
- impact_justifications                (input_context : comment + feature_type + feature + impact_criteria, impact)
- urgency_justifications               (input_context : comment + feature_type + feature + urgency_criteria, urgency)
- feature_priority_score               (input_context : impact + urgency)
- moscow_category_result               (input_context : feature_priority_score)
- feature_recommendation_justification (input_context : comment+impact+urgency+feature_priority_score+MoSCoW_category_result)


Agent 3: Story Writer
Input:
- comment
- feature
- feature_type
- feature_recommendation_justification

Output 1: 
- user story (input_context : feature+impact+urgency+template)
- development_complexity_estimation (input_context : feature, feature_type, feature_recommendation_justification, complexity_factors)

output 2: 
- feature_acceptance_criteria (input_context : comment + template)



Complete final output for the user : 
final_output : 