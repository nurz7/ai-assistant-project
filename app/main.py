from fastapi import FastAPI

from app.api.routes.chat import router as chat_router
from app.api.routes.reports import router as reports_router

APP_VERSION = "0.4.0"

app = FastAPI(
    title="AI/GIS Copilot for Reservoir Monitoring",
    description="AI/GIS assistant prototype for reservoir monitoring workflows",
    version=APP_VERSION,
)

app.include_router(chat_router)
app.include_router(reports_router)


@app.get("/")
async def home() -> dict[str, str]:
    return {
        "message": "AI/GIS Copilot for Reservoir Monitoring is running",
        "status": "ok",
        "version": APP_VERSION,
    }
