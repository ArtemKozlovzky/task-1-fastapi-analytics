from fastapi import Depends, APIRouter, HTTPException, Path
from sqlalchemy import select, func

from app.models import ModelOrm, OfferOrm, MakeOrm
from app.schemas import Statistics, StatisticsRequest, MakeStatistics
from app.database import get_session, AsyncSession
from app.utils.filters import to_single, to_list, apply_filters, extract_user_input


router = APIRouter()

@router.post("/analytics/stats", response_model=Statistics)
async def get_stats(
    query_params: StatisticsRequest,
    session: AsyncSession = Depends(get_session)
):
    user_input = extract_user_input(query_params)

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

    stats_q = select(
        func.count().label("total_offers"),
        func.avg(OfferOrm.original_price).label("average_price"),
        func.avg(OfferOrm.mileage).label("average_mileage")
    )

    if make_id and not model_id:
        stats_q = stats_q.where(OfferOrm.make_id == make_id)
    elif make_id and model_id:
        stats_q = stats_q.where(OfferOrm.make_id == make_id)
        stats_q = stats_q.where(OfferOrm.model_id == model_id)

    stats_q = apply_filters(
        stats_q,
        min_price=user_input["min_price"],
        max_price=user_input["max_price"],
        min_mileage=user_input["min_mileage"],
        max_mileage=user_input["max_mileage"],
        engine_vals=to_list(user_input["engine_type_id"]),
        body_vals=to_list(user_input["body_type_id"]),
        trans_vals=to_list(user_input["transmission_type_id"])
    )

    result = await session.execute(stats_q)
    total_offers, average_price, average_mileage = result.one()

    return Statistics(
        total_offers=total_offers or 0,
        average_price=average_price,
        average_mileage=average_mileage
    )



@router.get("/analytics/by-make/{make_id}", response_model=MakeStatistics)
async def get_stats_by_make(
    make_id: int = Path(..., description="make id"),
    session: AsyncSession = Depends(get_session)
):
    make_q = select(MakeOrm).where(MakeOrm.make_id == make_id)
    make_result = await session.execute(make_q)
    make_obj = make_result.scalar_one_or_none()

    if not make_obj:
        raise HTTPException(status_code=404, detail="Make not found")

    stats_q = select(
        func.count().label("total_offers"),
        func.avg(OfferOrm.original_price).label("average_price"),
        func.avg(OfferOrm.mileage).label("average_mileage")
    ).where(OfferOrm.make_id == make_id)

    stats_result = await session.execute(stats_q)
    total_offers, average_price, average_mileage = stats_result.one()

    return MakeStatistics(
        make_id=make_id,
        make_name=make_obj.make_name,
        total_offers=total_offers or 0,
        average_price=average_price,
        average_mileage=average_mileage
    )
