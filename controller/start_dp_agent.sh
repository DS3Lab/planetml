@echo "Starting DataPerf Agents"
export $(grep -v '^#' controller/.dp.env | xargs -d '\n') && uvicorn dataperf_app:dataperf_app --port 5010 --host 0.0.0.0 --workers 1 --reload --app-dir src/agents/ --debug --reload-dir src/agents/