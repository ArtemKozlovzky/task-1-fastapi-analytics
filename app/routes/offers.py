from fastapi import HTTPException, Depends, Query, APIRouter, Path
from fastapi_pagination import Page, paginate
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import *
from app.schemas import *
from app.database import get_session, AsyncSession

router = APIRouter()

@router.get("/get_offers", response_model=Page[OfferSchema])
async def get_offers(
    session: AsyncSession = Depends(get_session),
    min_price: float = Query(None, description="minimal price"),
    max_price: float = Query(None, description="maximum price"),
    min_mileage: float = Query(None, description="minimal mileage"),
    max_mileage: float = Query(None, description="maximum mileage"),
    make_ids: list[int] = Query(None, description="make ids, separated by commas"),
    model_ids: list[int] = Query(None, description="model ids, separated by commas"),
    engine_type_ids: list[int] = Query(None, description="engine type ids, separated by commas"),
    body_type_ids: list[int] = Query(None, description="body type ids, separated by commas"),
    transmission_type_ids: list[int] = Query(None, description="transmission type ids, separated by commas"),
    sort_order_by_price: str = Query(None, regex="^(asc|desc|none)$", description="sort by price: asc or desc"),
    sort_order_by_mileage: str = Query(None, regex="^(asc|desc|none)$", description="sort by mileage: asc or desc"),
    sort_order_by_publication_date: str = Query(None, regex="^(asc|desc|none)$", description="sort by publication date: asc or desc")
):
    try:
        query = select(OfferOrm).options(
            joinedload(OfferOrm.make),
            joinedload(OfferOrm.model),
            joinedload(OfferOrm.color),
            joinedload(OfferOrm.body_type),
            joinedload(OfferOrm.engine_type),
            joinedload(OfferOrm.publication_type),
            joinedload(OfferOrm.transmission_type)
        )

        if min_price is not None:
            query = query.where(OfferOrm.original_price >= min_price)
        if max_price is not None:
            query = query.where(OfferOrm.original_price <= max_price)

        if min_mileage is not None:
            query = query.where(OfferOrm.mileage >= min_mileage)
        if max_mileage is not None:
            query = query.where(OfferOrm.mileage <= max_mileage)

        if make_ids:
            query = query.where(OfferOrm.make_id.in_(make_ids))

        if model_ids:
            query = query.where(OfferOrm.model_id.in_(model_ids))

        if engine_type_ids:
            query = query.where(OfferOrm.engine_type_id.in_(engine_type_ids))

        if body_type_ids:
            query = query.where(OfferOrm.body_type_id.in_(body_type_ids))

        if transmission_type_ids:
            query = query.where(OfferOrm.transmission_type_id.in_(transmission_type_ids))

        if sort_order_by_price == "asc":
            query = query.order_by(OfferOrm.original_price.asc())
        elif sort_order_by_price == "desc":
            query = query.order_by(OfferOrm.original_price.desc())
        elif sort_order_by_price == "none":
            query = query.order_by(None)

        if sort_order_by_mileage == "asc":
            query = query.order_by(OfferOrm.mileage.asc())
        elif sort_order_by_mileage == "desc":
            query = query.order_by(OfferOrm.mileage.desc())
        elif sort_order_by_mileage == "none":
            query = query.order_by(None)

        if sort_order_by_publication_date == "asc":
            query = query.order_by(OfferOrm.publication_create_date.asc())
        elif sort_order_by_publication_date == "desc":
            query = query.order_by(OfferOrm.publication_create_date.desc())
        elif sort_order_by_publication_date == "none":
            query = query.order_by(None)

        results = await session.execute(query)
        offers = results.scalars().all()

        response_list = []
        for offer in offers:
            response_list.append(
                OfferSchema(
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
            )
        return paginate(response_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offer/{offer_id}", response_model=OfferSchema)
async def get_offer_by_id(
    offer_id: int = Path(..., description="offer id"),
    session: AsyncSession = Depends(get_session)
):
    try:
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
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))