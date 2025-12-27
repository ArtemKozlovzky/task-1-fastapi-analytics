from fastapi_pagination import Page, Params, add_pagination
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException, APIRouter, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import *
from app.schemas import *
from app.database import get_session

router = APIRouter()
add_pagination(router)

@router.post("/offers", response_model=Page[OfferSchema])
async def offers(query_params: OfferQueryParams, session: AsyncSession = Depends(get_session)):
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
        "sort_by": query_params.sort_by,
        "sort_direction": query_params.sort_direction
    }

    page = int(getattr(query_params, "page", 1) or 1)
    size = int(getattr(query_params, "size", 20) or 20)
    if page < 1:
        page = 1
    if size < 1:
        size = 20
    offset = (page - 1) * size

    def to_list(v):
        if v is None:
            return None
        if isinstance(v, (list, tuple, set)):
            vals = list(v)
        else:
            vals = [v]
        return vals if vals else None

    make_vals = to_list(user_input["make_id"])
    model_vals = to_list(user_input["model_id"])
    engine_vals = to_list(user_input["engine_type_id"])
    body_vals = to_list(user_input["body_type_id"])
    trans_vals = to_list(user_input["transmission_type_id"])

    if model_vals and not make_vals:
        raise HTTPException(status_code=400, detail="model_id cannot be provided without make_id")

    query = select(OfferOrm).options(
        joinedload(OfferOrm.make),
        joinedload(OfferOrm.model),
        joinedload(OfferOrm.color),
        joinedload(OfferOrm.body_type),
        joinedload(OfferOrm.engine_type),
        joinedload(OfferOrm.publication_type),
        joinedload(OfferOrm.transmission_type)
    )

    if user_input["min_price"] is not None:
        query = query.where(OfferOrm.original_price >= user_input["min_price"])
    if user_input["max_price"] is not None:
        query = query.where(OfferOrm.original_price <= user_input["max_price"])

    if user_input["min_mileage"] is not None:
        query = query.where(OfferOrm.mileage >= user_input["min_mileage"])
    if user_input["max_mileage"] is not None:
        query = query.where(OfferOrm.mileage <= user_input["max_mileage"])

    if make_vals:
        query = query.where(OfferOrm.make_id.in_(make_vals))

    if model_vals:
        query = query.where(OfferOrm.model_id.in_(model_vals))

    if engine_vals:
        query = query.where(OfferOrm.engine_type_id.in_(engine_vals))

    if body_vals:
        query = query.where(OfferOrm.body_type_id.in_(body_vals))

    if trans_vals:
        query = query.where(OfferOrm.transmission_type_id.in_(trans_vals))

    if user_input["sort_by"] == "price":
        if user_input["sort_direction"] == "asc":
            query = query.order_by(OfferOrm.original_price.asc())
        elif user_input["sort_direction"] == "desc":
            query = query.order_by(OfferOrm.original_price.desc())
    elif user_input["sort_by"] == "mileage":
        if user_input["sort_direction"] == "asc":
            query = query.order_by(OfferOrm.mileage.asc())
        elif user_input["sort_direction"] == "desc":
            query = query.order_by(OfferOrm.mileage.desc())
    elif user_input["sort_by"] == "publication_date":
        if user_input["sort_direction"] == "asc":
            query = query.order_by(OfferOrm.publication_create_date.asc())
        elif user_input["sort_direction"] == "desc":
            query = query.order_by(OfferOrm.publication_create_date.desc())

    count_q = select(func.count()).select_from(OfferOrm)
    if user_input["min_price"] is not None:
        count_q = count_q.where(OfferOrm.original_price >= user_input["min_price"])
    if user_input["max_price"] is not None:
        count_q = count_q.where(OfferOrm.original_price <= user_input["max_price"])
    if user_input["min_mileage"] is not None:
        count_q = count_q.where(OfferOrm.mileage >= user_input["min_mileage"])
    if user_input["max_mileage"] is not None:
        count_q = count_q.where(OfferOrm.mileage <= user_input["max_mileage"])
    if make_vals:
        count_q = count_q.where(OfferOrm.make_id.in_(make_vals))
    if model_vals:
        count_q = count_q.where(OfferOrm.model_id.in_(model_vals))
    if engine_vals:
        count_q = count_q.where(OfferOrm.engine_type_id.in_(engine_vals))
    if body_vals:
        count_q = count_q.where(OfferOrm.body_type_id.in_(body_vals))
    if trans_vals:
        count_q = count_q.where(OfferOrm.transmission_type_id.in_(trans_vals))

    total_result = await session.execute(count_q)
    total = int(total_result.scalar_one() or 0)

    paged_query = query.offset(offset).limit(size)
    results = await session.execute(paged_query)
    offers = results.scalars().all()

    def safe(obj, attr):
        return getattr(obj, attr, None) if obj is not None else None

    response_list = []
    for offer in offers:
        response_list.append(
            OfferSchema(
                offer_id=offer.offer_id,
                source_offer_id=offer.source_offer_id,
                make=safe(offer.make, "make_name"),
                model=safe(offer.model, "model_name"),
                title=offer.title,
                color=safe(offer.color, "color_name"),
                body_type=safe(offer.body_type, "body"),
                engine_type=safe(offer.engine_type, "engine"),
                engine_capacity=offer.engine_capacity,
                engine_power_kw=offer.engine_power_kw,
                engine_power_hp=offer.engine_power_hp,
                mileage=offer.mileage,
                transmission_type=safe(offer.transmission_type, "transmission"),
                year_of_issue=offer.year_of_issue,
                vin=offer.vin,
                original_price=offer.original_price,
                tax_deductible=offer.tax_deductible,
                first_registration=offer.first_registration,
                publication_create_date=offer.publication_create_date,
                publication_update_date=offer.publication_update_date,
                available_now=offer.available_now,
                publication_type=safe(offer.publication_type, "publication"),
                equipment=offer.equipment,
                description=offer.description,
                source_url=offer.source_url,
                created_at=offer.created_at,
                image_urls=offer.image_urls,
                city=offer.city,
                country=offer.country,
                seller_id=offer.seller_id
            )
        )

    params = Params(page=page, size=size)
    return Page.create(items=response_list, total=total, params=params)






@router.get("/offer/{offer_id}", response_model=OfferSchema)
async def get_offer_by_id(
    offer_id: int = Path(..., description="offer id"),
    session: AsyncSession = Depends(get_session)
):
    result = await session.execute(
        select(OfferOrm).options(
            joinedload(OfferOrm.make),
            joinedload(OfferOrm.model),
            joinedload(OfferOrm.color),
            joinedload(OfferOrm.body_type),
            joinedload(OfferOrm.engine_type),
            joinedload(OfferOrm.publication_type),
            joinedload(OfferOrm.transmission_type)
        ).where(OfferOrm.offer_id == offer_id)
    )
    offer = result.scalars().first()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    return OfferSchema(
        offer_id=offer.offer_id,
        source_offer_id=offer.source_offer_id,
        make=offer.make.make_name,
        model=offer.model.model_name,
        title=offer.title,
        color=offer.color.color_name,
        body_type=offer.body_type.body,
        engine_type=offer.engine_type.engine,
        engine_capacity=offer.engine_capacity,
        engine_power_kw=offer.engine_power_kw,
        engine_power_hp=offer.engine_power_hp,
        mileage=offer.mileage,
        transmission_type=offer.transmission_type.transmission,
        year_of_issue=offer.year_of_issue,
        vin=offer.vin,
        original_price=offer.original_price,
        tax_deductible=offer.tax_deductible,
        first_registration=offer.first_registration,
        publication_create_date=offer.publication_create_date,
        publication_update_date=offer.publication_update_date,
        available_now=offer.available_now,
        publication_type=offer.publication_type.publication,
        equipment=offer.equipment,
        description=offer.description,
        source_url=offer.source_url,
        created_at=offer.created_at,
        image_urls=offer.image_urls,
        city=offer.city,
        country=offer.country,
        seller_id=offer.seller_id
    )