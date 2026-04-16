# run the backend from the project root (not from src/summary_chatbot)
# PYTHONPATH=src uv run uvicorn summary_chatbot.main:app --reload

# run the frontend (using streamlit). Run the command in the app folder.
# streamlit run app.py

# update project structure file :
# tree -a --filelimit 100 --dirsfirst -I ".venv|.git|__pycache__|node_modules|.DS_Store" > project_structure.txt

# run the full Product Owner pipeline:
# uv run python tests/run_full_pipeline.py

# evaluate the full Product Owner pipeline against ground truth:
# uv run python tests/evaluation/evaluate_full_pipeline.py

# Why did i not use LangGraph? 
# I connected the agents through a typed sequential orchestration layer. 
# I did not use LangGraph in the MVP because the workflow is linear, 
# but the architecture keeps each step isolated so it can later be migrated to 
# a graph if branching, retries, or human validation are needed.

# sudo powermetrics --samplers gpu_power -i 1000 -n 5    