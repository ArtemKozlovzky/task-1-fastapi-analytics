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


@router.get("/analytics/price-distribution", response_model=PriceDistributionResponse)
async def price_distribution(
    min_price: int = 0,
    max_price: int = 100000,
    bucket_count: int = 10,
    make_id: int | None = None,
    model_id: int | None = None,
    engine_type_id: int | None = None,
    body_type_id: int | None = None,
    transmission_type_id: int | None = None,
    session: AsyncSession = Depends(get_session)
):

    if min_price >= max_price:
        raise HTTPException(
            status_code=400,
            detail="min_price must be less than max_price"
        )

    if bucket_count <= 0:
        raise HTTPException(
            status_code=400,
            detail="bucket_count must be positive"
        )

    bucket = func.width_bucket(
        OfferOrm.original_price,
        min_price,
        max_price,
        bucket_count
    )

    stmt = (
        select(
            bucket.label("bucket"),
            func.count().label("count")
        )
        .where(OfferOrm.original_price != None)
    )

    if make_id:
        stmt = stmt.where(OfferOrm.make_id == make_id)
    if model_id:
        stmt = stmt.where(OfferOrm.model_id == model_id)
    if engine_type_id:
        stmt = stmt.where(OfferOrm.engine_type_id == engine_type_id)
    if body_type_id:
        stmt = stmt.where(OfferOrm.body_type_id == body_type_id)
    if transmission_type_id:
        stmt = stmt.where(OfferOrm.transmission_type_id == transmission_type_id)

    stmt = stmt.where(bucket > 0).where(bucket <= bucket_count)

    stmt = stmt.group_by(bucket).order_by(bucket)

    rows = (await session.execute(stmt)).all()

    bucket_size = (max_price - min_price) / bucket_count

    buckets = []
    for row in rows:
        b = row.bucket
        buckets.append(
            PriceDistributionBucket(
                min_price=int(min_price + (b - 1) * bucket_size),
                max_price=int(min_price + b * bucket_size),
                count=row.count
            )
        )

    return PriceDistributionResponse(buckets=buckets)


