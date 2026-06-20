import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings
from app.routers import sites, incidents, health

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger("aiops")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("AIOps API starting up")
    yield
    logger.info("AIOps API shutting down")


app = FastAPI(
    title="AIOps Agent",
    description="Autonomous Incident Response System",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(sites.router, prefix="/api")
app.include_router(incidents.router, prefix="/api")


@app.get("/")
def root():
    return {"service": "aiops-agent", "docs": "/docs"}
