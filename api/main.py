from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.src.files.routes import router as files_router
from api.src.leases.routes import router as leases_router
from api.src.mock_routes import mock_router
from api.src.properties.routes import router as properties_router
from api.src.units.routes import router as units_router
from api.src.users.routes import router as auth_router
from api.utils.migrations import run_migrations

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    root_path="/api",
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(properties_router)
app.include_router(leases_router)
app.include_router(units_router)
app.include_router(files_router)

app.include_router(mock_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to RentEase API!"}
