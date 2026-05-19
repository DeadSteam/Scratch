"""Generic CRUD router factory.

Builds a standard list/get/create/update/delete router for a service that
follows the BaseService protocol. Used by the knowledge routers
(situations/causes/advices) to remove ~150 lines of copy-paste (B4).

Implementation note: we intentionally do NOT use
`from __future__ import annotations` here. With PEP 563 enabled, FastAPI
would call ``get_type_hints`` to resolve annotations from
``func.__globals__`` — and the schema/dep variables we use are closure
variables, not module globals. Annotations would resolve to ``None`` /
``Any`` and FastAPI would reject incoming requests with 422 because
it can't see the ``Depends(...)`` markers any more.

Without the future import, the annotations on the inner endpoint
functions are evaluated eagerly at definition time, capturing the actual
``Annotated[..., Depends(...)]`` objects. FastAPI sees them and wires up
DI correctly.

Static type checkers (mypy/ty) flag the pattern as ``invalid-type-form``;
those warnings are suppressed inline below.
"""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Query, status

from .responses import PaginatedResponse, Response


def make_crud_router(
    *,
    prefix: str,
    tag: str,
    create_schema: Any,
    update_schema: Any,
    read_schema: Any,
    service_dep: Any,
    session_dep: Any,
    auth_dep: Any,
    admin_dep: Any,
) -> APIRouter:
    """Construct a router with list/get/create/update/delete endpoints.

    Mutating endpoints (POST/PATCH/DELETE) require `admin_dep`. Read
    endpoints require `auth_dep`. Service/session deps are FastAPI
    `Annotated[...]` aliases (e.g. `SituationSvc`, `KnowledgeDBSession`).
    """
    router = APIRouter(prefix=prefix, tags=[tag])

    @router.get("/", response_model=PaginatedResponse[read_schema])
    async def list_items(        service: service_dep,
        db: session_dep,
        _user: auth_dep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000),
    ):
        items = await service.get_all(db, skip, limit)
        total = await service.count(db)
        return PaginatedResponse(
            success=True,
            data=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total,
        )

    @router.get("/{item_id}", response_model=Response[read_schema])
    async def get_item(        item_id: UUID,
        service: service_dep,
        db: session_dep,
        _user: auth_dep,
    ):
        item = await service.get_by_id(item_id, db)
        return Response(success=True, message="OK", data=item)

    @router.post(
        "/",
        response_model=Response[read_schema],
        status_code=status.HTTP_201_CREATED,
    )
    async def create_item(        data: create_schema,
        service: service_dep,
        db: session_dep,
        _admin: admin_dep,
    ):
        item = await service.create(data, db)
        return Response(success=True, message="Создано", data=item)

    @router.patch("/{item_id}", response_model=Response[read_schema])
    async def update_item(        item_id: UUID,
        data: update_schema,
        service: service_dep,
        db: session_dep,
        _admin: admin_dep,
    ):
        item = await service.update(item_id, data, db)
        return Response(success=True, message="Обновлено", data=item)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(        item_id: UUID,
        service: service_dep,
        db: session_dep,
        _admin: admin_dep,
    ):
        await service.delete(item_id, db)
        return None

    return router
