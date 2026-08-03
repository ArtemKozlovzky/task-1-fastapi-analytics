import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException

from app.routes.offers import get_offer_by_id
from app.schemas import OfferSchema

@pytest.mark.asyncio
async def test_get_offer_by_id_unit():
    fake_offer = MagicMock()
    fake_offer.offer_id = 1
    fake_offer.source_offer_id = "SRC1"
    fake_offer.title = "Test Offer"
    fake_offer.engine_capacity = 2.0
    fake_offer.engine_power_kw = 100
    fake_offer.engine_power_hp = 136
    fake_offer.mileage = 50000
    fake_offer.year_of_issue = 2020
    fake_offer.vin = "VIN123"
    fake_offer.original_price = 15000
    fake_offer.tax_deductible = True
    fake_offer.first_registration = "2025-10-20 00:00:00"
    fake_offer.publication_create_date = "2025-10-20 15:00:00"
    fake_offer.publication_update_date = "2025-10-20 15:00:00"
    fake_offer.available_now = True
    fake_offer.equipment = ["Test", "Test"]
    fake_offer.description = "Test description"
    fake_offer.source_url = "http://example.com"
    fake_offer.created_at = "2025-10-20 15:00:00"
    fake_offer.image_urls = ["http://example.com/img.jpg"]
    fake_offer.city = "Minsk"
    fake_offer.country = "Belarus"
    fake_offer.seller_id = 1

    fake_offer.make = MagicMock(make_name="TestMake")
    fake_offer.model = MagicMock(model_name="TestModel")
    fake_offer.color = MagicMock(color_name="Red")
    fake_offer.body_type = MagicMock(body="Sedan")
    fake_offer.engine_type = MagicMock(engine="Petrol")
    fake_offer.transmission_type = MagicMock(transmission="Manual")
    fake_offer.publication_type = MagicMock(publication="Online")

    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = fake_offer

    fake_session = AsyncMock()
    fake_session.execute.return_value = fake_result

    result = await get_offer_by_id(1, session=fake_session)

    assert isinstance(result, OfferSchema)
    assert result.offer_id == 1
    assert result.make == "TestMake"
    assert result.model == "TestModel"


@pytest.mark.asyncio
async def test_get_offer_by_id_not_found():
    fake_result = MagicMock()
    fake_result.scalars.return_value.first.return_value = None

    fake_session = AsyncMock()
    fake_session.execute.return_value = fake_result

    with pytest.raises(HTTPException) as exc:
        await get_offer_by_id(999, session=fake_session)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Offer not found"


@pytest.mark.asyncio
async def test_get_offer_by_id_db_error():
    fake_session = AsyncMock()
    fake_session.execute.side_effect = Exception("DB error")

    with pytest.raises(Exception) as exc:
        await get_offer_by_id(1, session=fake_session)

    assert "DB error" in str(exc.value)