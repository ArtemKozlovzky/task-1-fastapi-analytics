import os
from fastapi import APIRouter
from typing import Any, Dict, List
from app.schemas import CarsHubRequest, CarsHub, OfferSchema

import httpx

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


def map_cars_hub_offer(raw: Dict[str, Any]) -> OfferSchema:

    offer_id = raw.get("offerId")

    return OfferSchema(
        offer_id=offer_id,
        source_offer_id=f"cars_hub_{offer_id}" if offer_id else None,
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
        year_of_issue=raw.get("yearOfIssue"),
        vin=raw.get("vin"),
        original_price=raw.get("originalPrice"),
        tax_deductible=raw.get("taxDeductible"),
        first_registration=raw.get("firstRegistration"),
        publication_create_date=raw.get("publicationCreateDate"),
        publication_update_date=raw.get("publicationUpdateDate"),
        available_now=raw.get("availableNow"),
        publication_type=raw.get("publicationType"),
        equipment=raw.get("equipment"),
        description=raw.get("description"),
        source_url=raw.get("sourceUrl"),
        created_at=None,
        image_urls=raw.get("images"),
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
            if req.make and req.model else None
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
        "bodyType": (
            [req.body_type] if req.body_type else None
        ),
        "engineType": (
            [req.engine_type] if req.engine_type else None
        ),
        "taxDeductible": req.tax_deductible,
        "excludeSponsored": True,
        "excludeUnavailable": True,
        "limit": req.limit,
    }
    return clean_payload(payload)


async def run_cars_hub_etl(req: CarsHubRequest) -> List[OfferSchema]:
    client = CarsHubClient()
    payload = build_offers_payload(req)
    raw = await client.get_offers(payload)
    offers_raw = raw.get("offers", [])

    mapped: List[OfferSchema] = [map_cars_hub_offer(o) for o in offers_raw]

    return mapped

@router.post("/test-api-endpoint", response_model=list[OfferSchema])
async def test_api_endpoint(req: CarsHubRequest):
    result = await run_cars_hub_etl(req)
    return result
