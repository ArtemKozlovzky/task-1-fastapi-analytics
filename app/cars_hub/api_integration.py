import os
from typing import Any, Dict, List

import httpx
from fastapi import APIRouter, BackgroundTasks
from sqlalchemy import select
from sqlalchemy.inspection import inspect
from sqlalchemy.dialects.postgresql import insert
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, date, timezone
import json

from app.schemas import CarsHubRequest, OfferSchema
from app.database import get_session
from app.models import (
    MakeOrm,
    ModelOrm,
    ColorOrm,
    BodyTypeOrm,
    EngineTypeOrm,
    TransmissionTypeOrm,
    PublicationTypeOrm,
    OfferOrm,
    SellerOrm
)

router = APIRouter()


class CarsHubClient:
    def __init__(self):
        self.base_url = os.getenv("CARS_HUB_BASE_URL")
        self.api_code = os.getenv("CARS_HUB_API_CODE")

    async def _get(self, path: str) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()

    async def _post(self, path: str, payload: Dict) -> Any:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                url,
                params={"code": self.api_code},
                json=payload,
                headers={"Content-Type": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def get_makes(self) -> List[Dict]:
        return await self._get("/makes")

    async def get_models(self, make: str) -> List[Dict]:
        return await self._get(f"/makes/{make}/models")

    async def get_body_types(self) -> List[Dict]:
        return await self._get("/body-types")

    async def get_transmission_types(self) -> List[Dict]:
        return await self._get("/transmission-types")

    async def get_engine_types(self) -> List[Dict]:
        return await self._get("/engine-types")

    async def get_offers(self, payload: Dict) -> Dict:
        data = await self._post("/offers", payload)
        return data or {"offers": []}

async def get_or_create_seller(session, seller_raw):
    if not seller_raw:
        return None

    seller_id = seller_raw.get("id")
    if not seller_id:
        return None

    try:
        seller_id = int(seller_id)
    except:
        print("Invalid seller_id:", seller_id)
        return None

    stmt = select(SellerOrm).where(SellerOrm.seller_id == seller_id)
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()

    if obj:
        return obj

    address_id = seller_raw.get("addressId")
    if address_id is not None:
        try:
            address_id = int(address_id)
        except:
            address_id = None

    phones = seller_raw.get("phoneFormattedNumbers")
    if isinstance(phones, list):
        phone_numbers = phones
    elif isinstance(phones, str):
        phone_numbers = [phones]
    else:
        phone_numbers = None

    obj = SellerOrm(
        seller_id=seller_id,
        source_seller_id=seller_raw.get("sellId"),
        seller_company_name=seller_raw.get("companyName"),
        seller_contact_name=seller_raw.get("contactName"),
        seller_sell_id=seller_raw.get("sellId"),
        seller_email=seller_raw.get("email"),
        seller_phone_formatted_numbers=phone_numbers,
        seller_address_id=address_id,
        seller_dealer_region=seller_raw.get("dealerRegion"),
        seller_dealer_homepage_url=seller_raw.get("dealerHomepageUrl"),
        seller_dealer_review_count=seller_raw.get("dealerReviewCount"),
        seller_dealer_rating_average=seller_raw.get("dealerRatingAverage"),
        seller_dealer_recommend_percentage=seller_raw.get("dealerRecommendPercentage"),
        seller_link_car_methods=seller_raw.get("linkCarMethods"),
        dealer_contact_person_phone=seller_raw.get("employer", {}).get("dealerContactPersonPhone"),
        dealer_contact_person_email=seller_raw.get("employer", {}).get("dealerContactPersonEmail"),
        dealer_contact_person_name=seller_raw.get("employer", {}).get("dealerContactPersonName"),
        dealer_contact_person_position=seller_raw.get("employer", {}).get("dealerContactPersonPosition"),
        seller_type_id=None,
    )

    session.add(obj)
    await session.flush()
    return obj



def parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except:
        pass
    try:
        return datetime.fromisoformat(value.replace("Z", "")).date()
    except:
        return None


from datetime import datetime, date, timezone

def parse_datetime(value):
    if not value:
        return None

    value = value.replace("Z", "+00:00")

    try:
        dt = datetime.fromisoformat(value)
    except:
        try:
            dt = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
        except:
            return None

    if isinstance(dt, date) and not isinstance(dt, datetime):
        dt = datetime(dt.year, dt.month, dt.day, tzinfo=timezone.utc)

    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

    return dt


def map_cars_hub_offer(raw: Dict[str, Any]) -> OfferSchema:
    first_reg = parse_date(raw.get("firstRegistration"))
    pub_create = parse_datetime(raw.get("publicationCreateDate"))
    pub_update = parse_datetime(raw.get("publicationUpdateDate"))
    created = parse_datetime(raw.get("createdAt"))
    imgs = raw.get("images")
    if isinstance(imgs, str):
        imgs = [imgs]
    eq = raw.get("equipment")
    if isinstance(eq, str):
        eq = [eq]
    year = raw.get("yearOfIssue")
    try:
        year = int(year) if year is not None else None
    except:
        year = None
    return OfferSchema(
        source_offer_id=f"cars_hub_{raw.get('offerId')}",
        make=raw.get("make"),
        model=raw.get("model"),
        title=raw.get("title"),
        color=raw.get("color"),
        body_type=raw.get("bodyType"),
        engine_type=raw.get("engineType"),
        engine_capacity=raw.get("engineCapacityRaw"),
        engine_power_kw=raw.get("engineHorsePowerInKw"),
        engine_power_hp=raw.get("engineHorsePowerInHp"),
        mileage=raw.get("mileage"),
        transmission_type=raw.get("transmissionType"),
        year_of_issue=year,
        vin=raw.get("vin"),
        original_price=raw.get("originalPrice"),
        tax_deductible=raw.get("taxDeductible"),
        first_registration=first_reg,
        publication_create_date=pub_create,
        publication_update_date=pub_update,
        available_now=raw.get("availableNow"),
        publication_type=raw.get("publicationType"),
        equipment=eq,
        description=raw.get("description"),
        source_url=raw.get("sourceUrl"),
        created_at=created,
        image_urls=imgs,
        city=raw.get("city"),
        country=raw.get("country"),
        seller_id=(raw.get("seller") or {}).get("id"),
    )


def is_placeholder(value):
    if isinstance(value, str) and value.lower() == "string":
        return True
    if isinstance(value, (int, float)) and value == 0:
        return True
    if isinstance(value, list) and all(is_placeholder(v) for v in value):
        return True
    if isinstance(value, dict) and all(is_placeholder(v) for v in value.values()):
        return True
    return False


def clean_payload(d: dict):
    cleaned = {}
    for k, v in d.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        if isinstance(v, (list, dict)) and len(v) == 0:
            continue
        if is_placeholder(v):
            continue
        cleaned[k] = v
    return cleaned


def build_offers_payload(req: CarsHubRequest) -> Dict:
    payload = {
        "carModels": (
            [{"make": req.make, "model": req.model}]
            if req.make and req.model
            else None
        ),
        "equipment": req.equipment or None,
        "toMileage": req.max_mileage,
        "fromMileage": req.min_mileage,
        "fromYear": req.min_year,
        "toYear": req.max_year,
        "fromPowerInKw": req.min_power_kw,
        "toPowerInKw": req.max_power_kw,
        "transmissionType": (
            [req.transmission_type] if req.transmission_type else None
        ),
        "bodyType": ([req.body_type] if req.body_type else None),
        "engineType": ([req.engine_type] if req.engine_type else None),
        "taxDeductible": req.tax_deductible,
        "excludeSponsored": True,
        "excludeUnavailable": True,
        "limit": min(req.limit or 50, 50),
    }
    return clean_payload(payload)


LOOKUP_FIELDS = {
    MakeOrm: "make_name",
    ModelOrm: "model_name",
    ColorOrm: "color_name",
    BodyTypeOrm: "body",
    EngineTypeOrm: "engine",
    TransmissionTypeOrm: "transmission",
    PublicationTypeOrm: "publication",
}


async def get_or_create(session, model, value):
    if value is None or (isinstance(value, str) and not value.strip()):
        return None

    field = LOOKUP_FIELDS[model]
    mapper = inspect(model)
    column = mapper.columns[field]

    stmt = select(model).where(column == value)
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()

    if obj:
        return obj

    obj = model(**{field: value})
    session.add(obj)
    await session.flush()
    return obj


async def get_or_create_model(session, model_name: str | None, make_obj: MakeOrm | None):
    if model_name is None or make_obj is None:
        return None

    stmt = select(ModelOrm).where(
        ModelOrm.model_name == model_name,
        ModelOrm.make_id == make_obj.make_id,
    )
    result = await session.execute(stmt)
    obj = result.scalar_one_or_none()

    if obj:
        return obj

    obj = ModelOrm(model_name=model_name, make_id=make_obj.make_id)
    session.add(obj)
    await session.flush()
    return obj


async def lookup_all(raw: OfferSchema) -> Dict[str, Any]:
    async with get_session() as session:
        make = await get_or_create(session, MakeOrm, raw.make)
        model = await get_or_create_model(session, raw.model, make)

        color = await get_or_create(session, ColorOrm, raw.color)
        body = await get_or_create(session, BodyTypeOrm, raw.body_type)
        engine = await get_or_create(session, EngineTypeOrm, raw.engine_type)
        transmission = await get_or_create(
            session, TransmissionTypeOrm, raw.transmission_type
        )
        publication = await get_or_create(
            session, PublicationTypeOrm, raw.publication_type
        )

        await session.commit()

        return {
            "make_id": make.make_id if make else None,
            "model_id": model.model_id if model else None,
            "color_id": color.color_id if color else None,
            "body_type_id": body.body_id if body else None,
            "engine_type_id": engine.engine_type_id if engine else None,
            "transmission_type_id": transmission.transmission_type_id
            if transmission
            else None,
            "publication_type_id": publication.publication_type_id
            if publication
            else None,
        }


async def upsert_offers(offers: list[dict]):
    async with get_session() as session:
        offer_columns = {col.name for col in OfferOrm.__table__.c}

        for raw in offers:
            mapped = map_cars_hub_offer(raw)
            data = mapped.model_dump()

            db_data = {k: v for k, v in data.items() if k in offer_columns}

            seller_raw = raw.get("seller")
            seller_obj = await get_or_create_seller(session, seller_raw)

            db_data["seller_id"] = seller_obj.seller_id if seller_obj else None

            db_data.pop("offer_id", None)

            if not db_data.get("source_offer_id"):
                print("SKIP: no source_offer_id")
                continue

            update_data = {k: v for k, v in db_data.items() if k != "offer_id"}

            stmt = (
                insert(OfferOrm)
                .values(**db_data)
                .on_conflict_do_update(
                    index_elements=["source_offer_id"],
                    set_=update_data,
                )
            )
            await session.execute(stmt)

        await session.commit()



async def run_cars_hub_etl(req: CarsHubRequest):
    client = CarsHubClient()
    payload = build_offers_payload(req)
    raw = await client.get_offers(payload)
    offers_raw = raw.get("offers", [])

    await upsert_offers(offers_raw)

    mapped = [map_cars_hub_offer(o) for o in offers_raw]

    final_data = []
    for offer in mapped:
        lookup_ids = await lookup_all(offer)
        merged = offer.model_dump()
        merged.update(lookup_ids)
        final_data.append(merged)

    return final_data



scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", minutes=30)
async def scheduled_sync():
    req = CarsHubRequest(limit=50)
    await run_cars_hub_etl(req)


def start_scheduler():
    scheduler.start()


@router.post("/test-api-endpoint", response_model=list[OfferSchema])
async def test_api_endpoint(req: CarsHubRequest):
    result = await run_cars_hub_etl(req)
    return result


@router.post("/internal/cars-hub/sync", status_code=202)
async def sync_on_demand(req: CarsHubRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_cars_hub_etl, req)
    return {"status": "accepted"}