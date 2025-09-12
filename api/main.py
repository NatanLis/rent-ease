from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.core.config import settings
from api.core.logging import get_logger, setup_logging
from api.src.files.routes import router as files_router
from api.src.leases.routes import router as leases_router
from api.src.payments.routes import router as payments_router
from api.src.profile_pictures.routes import router as profile_pictures_router
from api.src.properties.routes import router as properties_router
from api.src.tenants.routes import router as tenants_router
from api.src.units.routes import router as units_router
from api.src.users.auth_routes import router as auth_router
from api.src.users.routes import users_router
from api.utils.migrations import run_migrations

setup_logging()  # Initialize global logging for the application

run_migrations()  # Run database migrations at startup (can be disabled in config)

logger = get_logger(__name__)  # Logger instance for this module

app = FastAPI(
    root_path="/api",
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # WARNING: In production, specify allowed origins for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(properties_router)
app.include_router(leases_router)
app.include_router(units_router)
app.include_router(files_router)
app.include_router(profile_pictures_router)
app.include_router(tenants_router)
app.include_router(payments_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/")
async def root():
    """Root endpoint."""
    logger.debug("Root endpoint called")
    return {"message": "Welcome to RentEase API!"}
