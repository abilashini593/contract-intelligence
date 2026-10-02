import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.config import settings
from app.database import engine, init_db
from app.api import contracts_router, items_router, reminders_router, summary_router
from app.schemas.summary import LEGAL_DISCLAIMER_TEXT

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("contract_intelligence")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing database schema...")
    try:
        init_db()
        logger.info("Database schema initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}", exc_info=True)
    yield
    logger.info("Shutting down application...")

app = FastAPI(
    title="Contract Intelligence — Administrative Information Management Platform",
    description=(
        "Production-grade contract administrative tracking and information-management system. "
        "Extracts parties, key dates, clauses, obligations, and ambiguous terms with precise citations, "
        "maintains deterministic reminder schedules, and preserves contract versions. "
        "\n\n**LEGAL NOTICE**: This application is strictly an information-management tool and does NOT provide legal advice."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(contracts_router)
app.include_router(items_router)
app.include_router(reminders_router)
app.include_router(summary_router)

@app.get("/api/health", tags=["Health"])
def health_check():
    """Returns application health, database connectivity status, and legal disclaimer."""
    db_healthy = False
    db_error = None
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            db_healthy = True
    except Exception as e:
        db_error = str(e)

    return {
        "status": "healthy" if db_healthy else "database_unavailable",
        "database_connected": db_healthy,
        "database_error": db_error,
        "gemini_configured": bool(settings.GEMINI_API_KEY and "your_gemini" not in settings.GEMINI_API_KEY),
        "disclaimer": LEGAL_DISCLAIMER_TEXT,
        "application_type": "Information Management Tool (Not Legal Advice)"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error processing {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": f"An internal server error occurred: {str(exc)}"}
    )
