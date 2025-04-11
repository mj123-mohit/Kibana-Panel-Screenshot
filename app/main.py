# app/main.py

import logging
from fastapi import FastAPI
from app.api.routes import router as api_router

logging.basicConfig(level=logging.INFO)

def create_app() -> FastAPI:
    app = FastAPI(
        title="Kibana Screenshot API",
        description="APIs to list Kibana dashboards, panels, and take screenshots.",
        version="1.0.0",
    )
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=False)
