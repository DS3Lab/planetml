@echo "Starting planetmld.sh"
export $(grep -v '^#' controller/.dp.env | xargs -d '\n') && uvicorn app:app --port 5005 --host 0.0.0.0 --workers 2 --reload --app-dir src/backend --reload