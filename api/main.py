from fastapi import FastAPI

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.src.users.routes import router as auth_router
from api.src.properties.routes import router as properties_router
from api.src.leases.routes import router as leases_router
from api.src.units.routes import router as units_router

from api.utils.migrations import run_migrations

from api.upload import router as upload_router  # Dodano import routera upload

# Set up logging configuration
setup_logging()

# Optional: Run migrations on startup
run_migrations()

# Set up logger for this module
logger = get_logger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

# Include routers
app.include_router(auth_router)
app.include_router(properties_router)
app.include_router(leases_router)
app.include_router(units_router)
app.include_router(upload_router, prefix="/api")  # Dodano router uploadu

@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to RentEase API!"}  