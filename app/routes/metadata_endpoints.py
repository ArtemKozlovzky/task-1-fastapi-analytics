from fastapi import HTTPException, Depends, Query, APIRouter, Path
from fastapi_pagination import Page, paginate
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.models import *
from app.schemas import *
from app.database import get_session, AsyncSession

router = APIRouter()

@router.get("/get_makes", response_model=Page[BaseMake])
async def get_makes(session: AsyncSession = Depends(get_session)):
    try:
        query = select(MakeOrm)
        results = await session.execute(query)
        makes = results.scalars().all()
        response_list = []
        for make in makes:
            response_list.append(
                BaseMake(
                    make_id=make.make_id,
                    make_name=make.make_name
                )
            )
        return paginate(response_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_models", response_model=Page[SBaseModel])
async def get_models(
        make_id: int = Query(..., description="make id"),
        session: AsyncSession = Depends(get_session)
):
    query = select(ModelOrm).where(ModelOrm.make_id == make_id)
    results = await session.execute(query)
    models = results.scalars().all()
    response_list = [
        SBaseModel(
            model_id=model.model_id,
            model_name=model.model_name,
            make_id=model.make_id
        )
        for model in models
    ]
    return paginate(response_list)

@router.get("/get_body_types", response_model=Page[BaseBodyType])
async def get_body_types(session: AsyncSession = Depends(get_session)):
    try:
        query = select(BodyTypeOrm)
        results = await session.execute(query)
        body_types = results.scalars().all()
        response_list = []
        for body_type in body_types:
            response_list.append(
                BaseBodyType(
                    body_id=body_type.body_id,
                    body=body_type.body
                )
            )
        return paginate(response_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_transmission_types", response_model=Page[BaseTransmissionType])
async def get_transmission_types(session: AsyncSession = Depends(get_session)):
    try:
        query = select(TransmissionTypeOrm)
        results = await session.execute(query)
        transmission_types = results.scalars().all()
        response_list = []
        for transmission_type in transmission_types:
            response_list.append(
                BaseTransmissionType(
                    transmission_type_id=transmission_type.transmission_type_id,
                    transmission=transmission_type.transmission
                )
            )
        return paginate(response_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get_engine_types", response_model=Page[BaseEngineType])
async def get_engine_types(session: AsyncSession = Depends(get_session)):
    try:
        query = select(EngineTypeOrm)
        results = await session.execute(query)
        engine_types = results.scalars().all()
        response_list = []
        for engine_type in engine_types:
            response_list.append(
                BaseEngineType(
                    engine_type_id=engine_type.engine_type_id,
                    engine=engine_type.engine
                )
            )
        return paginate(response_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))