from dataclasses import asdict

from fastapi import Depends, Query, APIRouter, HTTPException, Path
from sqlalchemy import select, func
from typing import List
from sqlalchemy.orm import joinedload

from app.models import *
from app.schemas import *
from app.database import get_session, AsyncSession
from app.routes.offers import apply_filters

router = APIRouter()

@router.post("/analytics/stats", response_model=List[Statistics])
async def get_stats(
    query_params: StatisticsRequest,
    session: AsyncSession = Depends(get_session)
):
    user_input = {
        "min_price": query_params.min_price,
        "max_price": query_params.max_price,
        "min_mileage": query_params.min_mileage,
        "max_mileage": query_params.max_mileage,
        "make_id": query_params.make_id,
        "model_id": query_params.model_id,
        "engine_type_id": query_params.engine_type_id,
        "body_type_id": query_params.body_type_id,
        "transmission_type_id": query_params.transmission_type_id,
    }

    def to_single(v):
        if v is None:
            return None
        if isinstance(v, (list, tuple, set)):
            if len(v) > 1:
                raise HTTPException(status_code=400, detail="Only one value allowed")
            return list(v)[0]
        return v

    def to_list(v):
        if v is None:
            return None
        if isinstance(v, (list, tuple, set)):
            vals = list(v)
        else:
            vals = [v]
        return vals if vals else None

    make_id = to_single(user_input["make_id"])
    model_id = to_single(user_input["model_id"])

    if model_id and not make_id:
        raise HTTPException(status_code=400, detail="model_id cannot be provided without make_id")

    if make_id and model_id:
        valid_models_q = select(ModelOrm.model_id).where(ModelOrm.make_id == make_id)
        valid_models_result = await session.execute(valid_models_q)
        valid_models = set(valid_models_result.scalars().all())

        if model_id not in valid_models:
            raise HTTPException(status_code=400, detail="model_id does not belong to given make_id")

    query = select(OfferOrm).options(
        joinedload(OfferOrm.make),
        joinedload(OfferOrm.model),
        joinedload(OfferOrm.color),
        joinedload(OfferOrm.body_type),
        joinedload(OfferOrm.engine_type),
        joinedload(OfferOrm.publication_type),
        joinedload(OfferOrm.transmission_type)
    )

    query = apply_filters(
        query,
        min_price=user_input["min_price"],
        max_price=user_input["max_price"],
        min_mileage=user_input["min_mileage"],
        max_mileage=user_input["max_mileage"],
        engine_vals=to_list(user_input["engine_type_id"]),
        body_vals=to_list(user_input["body_type_id"]),
        trans_vals=to_list(user_input["transmission_type_id"])
    )

    if make_id and not model_id:
        query = query.where(OfferOrm.make_id == make_id)
    elif make_id and model_id:
        query = query.where(OfferOrm.make_id == make_id)
        query = query.where(OfferOrm.model_id == model_id)

    if user_input["min_price"] is not None:
        query = query.where(OfferOrm.original_price >= user_input["min_price"])
    if user_input["max_price"] is not None:
        query = query.where(OfferOrm.original_price <= user_input["max_price"])
    if user_input["min_mileage"] is not None:
        query = query.where(OfferOrm.mileage >= user_input["min_mileage"])
    if user_input["max_mileage"] is not None:
        query = query.where(OfferOrm.mileage <= user_input["max_mileage"])

    count_q = select(func.count()).select_from(OfferOrm)
    count_q = apply_filters(
        count_q,
        min_price=user_input["min_price"],
        max_price=user_input["max_price"],
        min_mileage=user_input["min_mileage"],
        max_mileage=user_input["max_mileage"],
        engine_vals=to_list(user_input["engine_type_id"]),
        body_vals=to_list(user_input["body_type_id"]),
        trans_vals=to_list(user_input["transmission_type_id"])
    )
    if make_id and not model_id:
        count_q = count_q.where(OfferOrm.make_id == make_id)
    elif make_id and model_id:
        count_q = count_q.where(OfferOrm.make_id == make_id)
        count_q = count_q.where(OfferOrm.model_id == model_id)

    total_result = await session.execute(count_q)
    total_offers = total_result.scalar_one() or 0

    avg_q = select(
        func.avg(OfferOrm.original_price),
        func.avg(OfferOrm.mileage)
    )
    avg_q = apply_filters(
        avg_q,
        min_price=user_input["min_price"],
        max_price=user_input["max_price"],
        min_mileage=user_input["min_mileage"],
        max_mileage=user_input["max_mileage"],
        engine_vals=to_list(user_input["engine_type_id"]),
        body_vals=to_list(user_input["body_type_id"]),
        trans_vals=to_list(user_input["transmission_type_id"])
    )
    if make_id and not model_id:
        avg_q = avg_q.where(OfferOrm.make_id == make_id)
    elif make_id and model_id:
        avg_q = avg_q.where(OfferOrm.make_id == make_id)
        avg_q = avg_q.where(OfferOrm.model_id == model_id)

    avg_result = await session.execute(avg_q)
    average_price, average_mileage = avg_result.one_or_none() or (None, None)

    response_list = [
        Statistics(
            total_offers=total_offers,
            average_price=average_price,
            average_mileage=average_mileage
        )
    ]
    return response_list

@router.get("/analytics/by-make/{make_id}", response_model=List[MakeStatistics])
async def get_stats_by_make(
        make_id: int = Path(..., description="make id"),
        session: AsyncSession = Depends(get_session)):

    count_q = select(func.count()).select_from(OfferOrm)
    count_q = count_q.where(OfferOrm.make_id == make_id)
    total_result = await session.execute(count_q)
    total_offers = total_result.scalar_one() or 0
    avg_q = select(
        func.avg(OfferOrm.original_price),
        func.avg(OfferOrm.mileage))
    avg_q = avg_q.where(OfferOrm.make_id == make_id)
    avg_result = await session.execute(avg_q)
    average_price, average_mileage = avg_result.one_or_none() or (None, None)
    query = select(MakeOrm).where(MakeOrm.make_id == make_id)
    result = await session.execute(query)
    make_obj = result.scalar_one_or_none()
    make_name = make_obj.make_name if make_obj else None
    response_list = [
        MakeStatistics (
            make_id=make_id,
            make_name=make_name,
            total_offers=total_offers,
            average_price=average_price,
            average_mileage=average_mileage
        )
    ]
    return response_list