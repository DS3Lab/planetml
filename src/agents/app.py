from fastapi import FastAPI
lc_app = FastAPI()

# the behavior of this script should be controlled by a config file - which agents should be loaded and supervised, etc.

@lc_app.get("/heartbeat/:id")
async def root():
    return {"message": "ok"}

@lc_app.get("/health")
async def health():
    return {"message": "ok"}

@lc_app.post("/node_join")
async def node_join():
    return {"message": "ok"}