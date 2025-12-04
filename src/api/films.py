"""Film management endpoints."""
from uuid import UUID
from fastapi import APIRouter, Query, status

from ..core.dependencies import FilmSvc, MainDBSession
from ..schemas.film import FilmCreate, FilmRead, FilmUpdate
from .responses import Response, PaginatedResponse

router = APIRouter(prefix="/films", tags=["Films"])


@router.get(
    "/",
    response_model=PaginatedResponse[FilmRead],
    summary="List films",
    description="Get paginated list of all films"
)
async def list_films(
    film_service: FilmSvc,
    db: MainDBSession,
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of items to return")
):
    """Get list of films with pagination."""
    films = await film_service.get_all(db, skip, limit)
    
    return PaginatedResponse(
        data=films,
        total=len(films),
        skip=skip,
        limit=limit,
        has_more=len(films) == limit
    )


@router.get(
    "/search",
    response_model=PaginatedResponse[FilmRead],
    summary="Search films by name",
    description="Search films by name pattern (case-insensitive)"
)
async def search_films(
    name: str = Query(..., min_length=1, description="Name pattern to search for"),
    film_service: FilmSvc = ...,
    db: MainDBSession = ...,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Search films by name pattern."""
    films = await film_service.search_by_name(name, db, skip, limit)
    
    return PaginatedResponse(
        data=films,
        total=len(films),
        skip=skip,
        limit=limit,
        has_more=len(films) == limit
    )


@router.get(
    "/{film_id}",
    response_model=Response[FilmRead],
    summary="Get film by ID",
    description="Retrieve a specific film by its ID"
)
async def get_film(
    film_id: UUID,
    film_service: FilmSvc,
    db: MainDBSession
):
    """Get film by ID."""
    film = await film_service.get_by_id(film_id, db)
    return Response(
        success=True,
        message="Film retrieved successfully",
        data=film
    )


@router.post(
    "/",
    response_model=Response[FilmRead],
    status_code=status.HTTP_201_CREATED,
    summary="Create film",
    description="Create a new film entry"
)
async def create_film(
    film_data: FilmCreate,
    film_service: FilmSvc,
    db: MainDBSession
):
    """Create a new film."""
    film = await film_service.create(film_data, db)
    return Response(
        success=True,
        message="Film created successfully",
        data=film
    )


@router.patch(
    "/{film_id}",
    response_model=Response[FilmRead],
    summary="Update film",
    description="Update film information"
)
async def update_film(
    film_id: UUID,
    film_data: FilmUpdate,
    film_service: FilmSvc,
    db: MainDBSession
):
    """Update film information."""
    film = await film_service.update(film_id, film_data, db)
    return Response(
        success=True,
        message="Film updated successfully",
        data=film
    )


@router.delete(
    "/{film_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete film",
    description="Permanently delete a film"
)
async def delete_film(
    film_id: UUID,
    film_service: FilmSvc,
    db: MainDBSession
):
    """Delete film."""
    await film_service.delete(film_id, db)
    return None





















