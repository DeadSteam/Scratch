"""Knowledge base API: situations, causes, advice."""

from uuid import UUID

from fastapi import APIRouter, Query, status

from ..core.dependencies import (
    AdviceSvc,
    CauseSvc,
    KnowledgeDBSession,
    SituationSvc,
)
from ..schemas.advice import AdviceCreate, AdviceRead, AdviceUpdate
from ..schemas.cause import CauseCreate, CauseRead, CauseUpdate
from ..schemas.situation import SituationCreate, SituationRead, SituationUpdate
from .responses import PaginatedResponse, Response

# --- Situations ---

router_situations = APIRouter(prefix="/situations", tags=["Situations"])


@router_situations.get("/", response_model=PaginatedResponse[SituationRead])
async def list_situations(
    situation_service: SituationSvc,
    db: KnowledgeDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    items = await situation_service.get_all(db, skip, limit)
    return PaginatedResponse(
        success=True,
        data=items,
        total=len(items),
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )


@router_situations.get("/{situation_id}", response_model=Response[SituationRead])
async def get_situation(
    situation_id: UUID,
    situation_service: SituationSvc,
    db: KnowledgeDBSession,
):
    item = await situation_service.get_by_id(situation_id, db)
    return Response(success=True, message="OK", data=item)


@router_situations.post(
    "/",
    response_model=Response[SituationRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_situation(
    data: SituationCreate,
    situation_service: SituationSvc,
    db: KnowledgeDBSession,
):
    item = await situation_service.create(data, db)
    return Response(success=True, message="Создано", data=item)


@router_situations.patch("/{situation_id}", response_model=Response[SituationRead])
async def update_situation(
    situation_id: UUID,
    data: SituationUpdate,
    situation_service: SituationSvc,
    db: KnowledgeDBSession,
):
    item = await situation_service.update(situation_id, data, db)
    return Response(success=True, message="Обновлено", data=item)


@router_situations.delete("/{situation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_situation(
    situation_id: UUID,
    situation_service: SituationSvc,
    db: KnowledgeDBSession,
):
    await situation_service.delete(situation_id, db)
    return None


@router_situations.get(
    "/{situation_id}/causes",
    response_model=PaginatedResponse[CauseRead],
)
async def list_causes_by_situation(
    situation_id: UUID,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    items = await cause_service.get_by_situation_id(situation_id, db, skip, limit)
    return PaginatedResponse(
        success=True,
        data=items,
        total=len(items),
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )


# --- Causes ---

router_causes = APIRouter(prefix="/causes", tags=["Causes"])


@router_causes.get("/", response_model=PaginatedResponse[CauseRead])
async def list_causes(
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    items = await cause_service.get_all(db, skip, limit)
    return PaginatedResponse(
        success=True,
        data=items,
        total=len(items),
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )


@router_causes.get("/{cause_id}", response_model=Response[CauseRead])
async def get_cause(
    cause_id: UUID,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
):
    item = await cause_service.get_by_id(cause_id, db)
    return Response(success=True, message="OK", data=item)


@router_causes.post(
    "/",
    response_model=Response[CauseRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_cause(
    data: CauseCreate,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
):
    item = await cause_service.create(data, db)
    return Response(success=True, message="Создано", data=item)


@router_causes.patch("/{cause_id}", response_model=Response[CauseRead])
async def update_cause(
    cause_id: UUID,
    data: CauseUpdate,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
):
    item = await cause_service.update(cause_id, data, db)
    return Response(success=True, message="Обновлено", data=item)


@router_causes.delete("/{cause_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cause(
    cause_id: UUID,
    cause_service: CauseSvc,
    db: KnowledgeDBSession,
):
    await cause_service.delete(cause_id, db)
    return None


@router_causes.get(
    "/{cause_id}/advices",
    response_model=PaginatedResponse[AdviceRead],
)
async def list_advices_by_cause(
    cause_id: UUID,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
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


# --- Advices ---

router_advices = APIRouter(prefix="/advices", tags=["Advices"])


@router_advices.get("/", response_model=PaginatedResponse[AdviceRead])
async def list_advices(
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
):
    items = await advice_service.get_all(db, skip, limit)
    return PaginatedResponse(
        success=True,
        data=items,
        total=len(items),
        skip=skip,
        limit=limit,
        has_more=len(items) == limit,
    )


@router_advices.get("/{advice_id}", response_model=Response[AdviceRead])
async def get_advice(
    advice_id: UUID,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
):
    item = await advice_service.get_by_id(advice_id, db)
    return Response(success=True, message="OK", data=item)


@router_advices.post(
    "/",
    response_model=Response[AdviceRead],
    status_code=status.HTTP_201_CREATED,
)
async def create_advice(
    data: AdviceCreate,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
):
    item = await advice_service.create(data, db)
    return Response(success=True, message="Создано", data=item)


@router_advices.patch("/{advice_id}", response_model=Response[AdviceRead])
async def update_advice(
    advice_id: UUID,
    data: AdviceUpdate,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
):
    item = await advice_service.update(advice_id, data, db)
    return Response(success=True, message="Обновлено", data=item)


@router_advices.delete("/{advice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_advice(
    advice_id: UUID,
    advice_service: AdviceSvc,
    db: KnowledgeDBSession,
):
    await advice_service.delete(advice_id, db)
    return None
