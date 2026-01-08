"""Structure tweak: renamed logger and static path identifiers while keeping FastAPI lifecycle and routes intact."""
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse

from config import settings
from database import cosmos_db
from routes_auth import router as auth_router
from routes_body_metrics import router as body_metrics_router
from routes_workouts import router as workouts_router
from routes_nutrition import router as nutrition_router
from routes_progress_photos import router as progress_photos_router
from routes_dashboard import router as dashboard_router
from storage import blob_storage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
app_logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    app_logger.info("Starting up Fitness Analytics Platform API...")
    try:
        cosmos_db.initialize()
        blob_storage.initialize()
        app_logger.info("Azure services initialized successfully")
    except Exception as e:  # noqa: BLE001 - surface initialization issues
        app_logger.error(f"Failed to initialize Azure services: {e}")
        raise

    yield

    app_logger.info("Shutting down Fitness Analytics Platform API...")


# Create FastAPI application
app = FastAPI(
    title="Fitness Analytics Platform API",
    description="REST API for fitness tracking, body metrics, workouts, and nutrition analysis",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Invalid request data",
                "details": str(exc),
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    app_logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.api_host == "0.0.0.0" else None,
            }
        },
    )


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Fitness Analytics Platform API",
        "version": "1.0.0",
    }


app.include_router(auth_router, prefix="/api")
app.include_router(body_metrics_router, prefix="/api")
app.include_router(workouts_router, prefix="/api")
app.include_router(nutrition_router, prefix="/api")
app.include_router(progress_photos_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

static_folder = Path(__file__).parent / "static"
if static_folder.exists():
    @app.get("/", tags=["Frontend"])
    async def serve_frontend():
        """Serve Angular frontend"""
        return FileResponse(static_folder / "index.html")

    @app.get("/{full_path:path}", tags=["Frontend"])
    async def serve_spa(full_path: str):
        """Serve Angular frontend for all non-API routes"""
        if full_path.startswith("api/"):
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"error": {"code": "NOT_FOUND", "message": "Endpoint not found"}}
            )

        file_path = static_folder / full_path
        if file_path.is_file():
            return FileResponse(file_path)

        return FileResponse(static_folder / "index.html")
else:
    @app.get("/", tags=["Root"])
    async def root():
        """Root endpoint"""
        return {
            "message": "Fitness Analytics Platform API",
            "version": "1.0.0",
            "docs": "/api/docs",
        }


if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,
        log_level="info",
    )
