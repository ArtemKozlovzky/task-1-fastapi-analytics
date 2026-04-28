from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime

class Offer(BaseModel):
    offer_id: int | None = None
    source_offer_id: str | None
    make: str | None
    model: str | None
    title: str | None
    color: str | None
    body_type: str | None
    engine_type: str | None
    engine_capacity: int | None
    engine_power_kw: int | None
    engine_power_hp: int | None
    mileage: int | None
    transmission_type: str | None
    year_of_issue: int | None
    vin: str | None
    original_price: int | None
    tax_deductible: bool | None
    first_registration: date | None
    publication_create_date: datetime | None
    publication_update_date: datetime | None
    available_now: bool | None
    publication_type: str | None
    equipment: list[str] | None
    description: str | dict | None
    source_url: str | None
    created_at: datetime | None
    image_urls: list[str] | None
    city: str | None
    country: str | None
    seller_id: int | None

class OfferSchema(Offer):
    class Config:
        from_attributes = True

class Seller(BaseModel):
    seller_id: int
    source_seller_id: int | None
    seller_company_name: str
    seller_contact_name: str | None
    seller_sell_id: str |None
    seller_email: str | None
    seller_phone_formatted_numbers: str | None
    seller_address_id: str | None
    seller_dealer_region: str | None
    seller_dealer_homepage_url: str | None
    seller_dealer_review_count: int | None
    seller_dealer_rating_average: float | None
    seller_dealer_recommend_percentage: int | None
    seller_link_car_methods: str | None
    dealer_contact_person_phone: int | None
    dealer_contact_person_email: str | None
    dealer_contact_person_name: str | None
    dealer_contact_person_position: str |None
    seller_type: str

class Make(BaseModel):
    make_id: int
    make_name: str

class SModel(BaseModel):
    model_id: int
    model_name: str
    make_id: int

class BodyType(BaseModel):
    body_id: int
    body: str

class TransmissionType(BaseModel):
    transmission_type_id: int
    transmission: str | None

class EngineType(BaseModel):
    engine_type_id: int
    engine: str

class OffersRequest(BaseModel):
    min_price: float | None = "null"
    max_price: float | None = "null"
    min_mileage: float | None = "null"
    max_mileage: float | None = "null"
    make_id: int | None = "null"
    model_id: int | None = "null"
    engine_type_id: int | None = "null"
    body_type_id: int | None = "null"
    transmission_type_id: int | None = "null"
    sort_by: str | None = "price"
    sort_direction: str | None = "asc"

class CarsHubRequest(BaseModel):
    equipment: Optional[List[str]] = None
    min_mileage: Optional[int] = None
    max_mileage: Optional[int] = None
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    min_power_kw: Optional[int] = None
    max_power_kw: Optional[int] = None
    engine_type: Optional[str] = None
    body_type: Optional[str] = None
    transmission_type: Optional[str] = None
    tax_deductible: Optional[bool] = None
    sort_by: Optional[str] = None
    sort_direction: Optional[str] = None
    make: Optional[str] = None
    model: Optional[str] = None
    limit: Optional[int] = None