# uvicorn app:lc_app --port 5000 --host 0.0.0.0 --workers 1 --reload --app-dir src/agents/ --debug --reload-dir src/agents/
uvicorn app:lc_app --port 5000 --host 0.0.0.0 --workers 1 --app-dir src/agents/ --debug