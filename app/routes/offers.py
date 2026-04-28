from fastapi_pagination import Page, Params, add_pagination
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from fastapi import Depends, HTTPException, APIRouter, Path, BackgroundTasks, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
import csv
import uuid
import logging
import os
from app.utils.filters import to_single, to_list, extract_user_input, apply_filters
from app.models import OfferOrm, ExportJobOrm, ModelOrm
from app.schemas import OfferSchema, OffersRequest
from app.database import get_session, new_session

router = APIRouter()
add_pagination(router)


logger = logging.getLogger(__name__)

MAX_EXPORT_ROWS = 100_000

async def generate_csv_file(params: dict, session_factory, file_path: str):
    async with session_factory() as session:
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

            query = apply_filters(
                query,
                min_price=params["min_price"],
                max_price=params["max_price"],
                min_mileage=params["min_mileage"],
                max_mileage=params["max_mileage"],
                engine_vals=params["engine_type_id"],
                body_vals=params["body_type_id"],
                trans_vals=params["transmission_type_id"]
            )

            if params["make_id"]:
                query = query.where(OfferOrm.make_id == params["make_id"])
            if params["model_id"]:
                query = query.where(OfferOrm.model_id == params["model_id"])

            limit = min(params.get("csv_limit") or MAX_EXPORT_ROWS, MAX_EXPORT_ROWS)
            query = query.limit(limit)

            result = await session.stream(query)

            with open(file_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "offer_id", "make", "model", "price", "mileage", "year", "city"
                ])

                async for partition in result.partitions(1000):
                    for row in partition:
                        o = row[0]
                        writer.writerow([
                            o.offer_id,
                            o.make.make_name if o.make else None,
                            o.model.model_name if o.model else None,
                            o.original_price,
                            o.mileage,
                            o.year_of_issue,
                            o.city
                        ])

            job = await session.get(ExportJobOrm, params["job_id"])
            job.status = "completed"
            await session.commit()

        except Exception as e:
            logger.exception(f"Export failed for job {params.get('job_id')}")

            job = await session.get(ExportJobOrm, params["job_id"])
            if job:
                job.status = "failed"
                await session.commit()

            raise e


@router.post("/offers", response_model=Page[OfferSchema])
async def offers(query_params: OffersRequest, session: AsyncSession = Depends(get_session)):
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

    if user_input["sort_by"] == "price":
        query = query.order_by(
            OfferOrm.original_price.asc() if user_input["sort_direction"] == "asc"
            else OfferOrm.original_price.desc()
        )
    elif user_input["sort_by"] == "mileage":
        query = query.order_by(
            OfferOrm.mileage.asc() if user_input["sort_direction"] == "asc"
            else OfferOrm.mileage.desc()
        )
    elif user_input["sort_by"] == "publication_date":
        query = query.order_by(
            OfferOrm.publication_create_date.asc() if user_input["sort_direction"] == "asc"
            else OfferOrm.publication_create_date.desc()
        )

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
    total = int(total_result.scalar_one() or 0)

    paged_query = query.offset(offset).limit(size)
    results = await session.execute(paged_query)
    offers = results.scalars().all()

    def safe(obj, attr):
        return getattr(obj, attr, None) if obj is not None else None

    response_list = [
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
        for offer in offers
    ]

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

EXPORT_DIR = os.getenv("EXPORT_DIR", "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)

@router.post("/offers/export", status_code=status.HTTP_202_ACCEPTED)
async def submit_background_export(
    query_params: Depends(extract_user_input),
    background_tasks: BackgroundTasks,
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
        "sort_by": query_params.sort_by,
        "sort_direction": query_params.sort_direction,
        "csv_limit": query_params.csv_limit
    }

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

    job_id = uuid.uuid4()
    file_path = os.path.join(EXPORT_DIR, f"{job_id}.csv")

    job = ExportJobOrm(
        job_id=job_id,
        status="pending",
        filters=user_input,
        file_path=file_path
    )
    session.add(job)
    await session.commit()

    background_tasks.add_task(
        generate_csv_file,
        params={**user_input, "job_id": job_id},
        session_factory=new_session,
        file_path=file_path
    )

    return {
        "status": "queued",
        "job_id": str(job_id)
    }


@router.get("/offers/export/{job_id}")
async def download_export(job_id: str, session: AsyncSession = Depends(get_session)):
    job = await session.get(ExportJobOrm, job_id)

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    if job.status == "pending":
        return {"status": "pending"}

    if job.status == "failed":
        return {"status": "failed"}

    file_path = str(job.file_path)

    if job.status == "completed":
        if not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="File missing")
        return FileResponse(
            path=file_path,
            media_type="text/csv",
            filename=f"export_{job_id}.csv"
        )
