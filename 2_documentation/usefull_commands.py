# run the backend from the project root (not from src/summary_chatbot)
# PYTHONPATH=src uv run uvicorn summary_chatbot.main:app --reload

# run the frontend (using streamlit). Run the command in the app folder.
# streamlit run app.py

# update project structure file :
# tree -a --filelimit 100 --dirsfirst -I ".venv|.git|__pycache__|node_modules|.DS_Store" > project_structure.txt