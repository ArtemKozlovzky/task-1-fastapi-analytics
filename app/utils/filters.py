from fastapi import HTTPException
from app.models import OfferOrm


def to_single(value):
    if value is None:
        return None

    if isinstance(value, (list, tuple, set)):
        if len(value) > 1:
            raise HTTPException(status_code=400, detail="Only one value allowed")
        return list(value)[0]

    return value


def to_list(value):
    if value is None:
        return None

    if isinstance(value, (list, tuple, set)):
        return list(value)

    return [value]


def extract_user_input(params):
    return {
        "min_price": params.min_price,
        "max_price": params.max_price,
        "min_mileage": params.min_mileage,
        "max_mileage": params.max_mileage,
        "make_id": params.make_id,
        "model_id": params.model_id,
        "engine_type_id": params.engine_type_id,
        "body_type_id": params.body_type_id,
        "transmission_type_id": params.transmission_type_id,
    }


def apply_filters(
    base_query,
    min_price=None,
    max_price=None,
    min_mileage=None,
    max_mileage=None,
    make_vals=None,
    model_vals=None,
    engine_vals=None,
    body_vals=None,
    trans_vals=None,
):
    if min_price is not None:
        base_query = base_query.where(OfferOrm.original_price >= min_price)
    if max_price is not None:
        base_query = base_query.where(OfferOrm.original_price <= max_price)

    if min_mileage is not None:
        base_query = base_query.where(OfferOrm.mileage >= min_mileage)
    if max_mileage is not None:
        base_query = base_query.where(OfferOrm.mileage <= max_mileage)

    if make_vals:
        base_query = base_query.where(OfferOrm.make_id.in_(make_vals))
    if model_vals:
        base_query = base_query.where(OfferOrm.model_id.in_(model_vals))
    if engine_vals:
        base_query = base_query.where(OfferOrm.engine_type_id.in_(engine_vals))
    if body_vals:
        base_query = base_query.where(OfferOrm.body_type_id.in_(body_vals))
    if trans_vals:
        base_query = base_query.where(OfferOrm.transmission_type_id.in_(trans_vals))

    return base_query