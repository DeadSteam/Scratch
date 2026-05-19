"""Knowledge base API: situations, causes, advice.

Routers are built from a generic factory (api/crud_factory.py, audit B4)
plus a handful of hand-rolled cross-reference endpoints (causes by
situation_id, advices by cause_id).
"""

from uuid import UUID

from fastapi import APIRouter, Query

from ..core.dependencies import (
    AdviceSvc,
    CauseSvc,
    CurrentAdmin,
    CurrentUser,
    KnowledgeDBSession,
    SituationSvc,
)
from ..schemas.advice import AdviceCreate, AdviceRead, AdviceUpdate
from ..schemas.cause import CauseCreate, CauseRead, CauseUpdate
from ..schemas.situation import SituationCreate, SituationRead, SituationUpdate
from .crud_factory import make_crud_router
from .crud_router import paginated_list_by_parent
from .responses import PaginatedResponse

# ---------------------------------------------------------------------------
# Situations
# ---------------------------------------------------------------------------
router_situations = make_crud_router(
    prefix="/situations",
    tag="Situations",
    create_schema=SituationCreate,
    update_schema=SituationUpdate,
    read_schema=SituationRead,
    service_dep=SituationSvc,
    session_dep=KnowledgeDBSession,
    auth_dep=CurrentUser,
    admin_dep=CurrentAdmin,
)


@router_situations.get(
    "/{situation_id}/causes",
    response_model=PaginatedResponse[CauseRead],
)
async def list_causes_by_situation(
    situation_id: UUID,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
    _user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    return await paginated_list_by_parent(
        situation_id,
        db,
        skip,
        limit,
        list_fn=cause_service.get_by_situation_id,
        count_fn=cause_service.count_by_situation_id,
    )


# ---------------------------------------------------------------------------
# Causes
# ---------------------------------------------------------------------------
router_causes = make_crud_router(
    prefix="/causes",
    tag="Causes",
    create_schema=CauseCreate,
    update_schema=CauseUpdate,
    read_schema=CauseRead,
    service_dep=CauseSvc,
    session_dep=KnowledgeDBSession,
    auth_dep=CurrentUser,
    admin_dep=CurrentAdmin,
)


@router_causes.get(
    "/{cause_id}/advices",
    response_model=PaginatedResponse[AdviceRead],
)
async def list_advices_by_cause(
    cause_id: UUID,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
    _user: CurrentUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    items = await advice_service.get_by_cause_id(cause_id, db, skip, limit)
    return PaginatedResponse(
        success=True,
        data=items,
        total=len(items),
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )


# ---------------------------------------------------------------------------
# Advices
# ---------------------------------------------------------------------------
router_advices = make_crud_router(
    prefix="/advices",
    tag="Advices",
    create_schema=AdviceCreate,
    update_schema=AdviceUpdate,
    read_schema=AdviceRead,
    service_dep=AdviceSvc,
    session_dep=KnowledgeDBSession,
    auth_dep=CurrentUser,
    admin_dep=CurrentAdmin,
)


# Keep APIRouter imported (factory returns one; this avoids ruff F401).
_ = APIRouter
