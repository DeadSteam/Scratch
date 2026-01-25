"""API routers."""

from fastapi import APIRouter

from . import (
    auth,
    equipment_configs,
    experiments,
    films,
    image_analysis,
    images,
    knowledge,
    users,
)

# Create main API router
api_router = APIRouter()

# Include all sub-routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(films.router)
api_router.include_router(equipment_configs.router)
api_router.include_router(experiments.router)
api_router.include_router(images.router)
api_router.include_router(image_analysis.router)
api_router.include_router(knowledge.router_situations)
api_router.include_router(knowledge.router_causes)
api_router.include_router(knowledge.router_advices)

__all__ = ["api_router"]
