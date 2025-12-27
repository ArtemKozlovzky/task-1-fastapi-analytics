from fastapi import Depends, Query, APIRouter
from sqlalchemy import select
from typing import List

from app.models import *
from app.schemas import *
from app.database import get_session, AsyncSession

router = APIRouter()

@router.get("/makes", response_model=List[Make])
async def get_makes(session: AsyncSession = Depends(get_session)):
    query = select(MakeOrm)
    results = await session.execute(query)
    makes = results.scalars().all()
    response_list = [
        Make(
            make_id=make.make_id,
            make_name=make.make_name
        ) for make in makes
    ]
    return response_list


@router.get("/models", response_model=List[SModel])
async def get_models(
        make_id: int = Query(..., description="make id"),
        session: AsyncSession = Depends(get_session)
):
    query = select(ModelOrm).where(ModelOrm.make_id == make_id)
    results = await session.execute(query)
    models = results.scalars().all()
    response_list = [
        SModel(
            model_id=model.model_id,
            model_name=model.model_name,
            make_id=model.make_id
        )
        for model in models
    ]
    return response_list

@router.get("/body_types", response_model=List[BodyType])
async def get_body_types(session: AsyncSession = Depends(get_session)):
    query = select(BodyTypeOrm)
    results = await session.execute(query)
    body_types = results.scalars().all()
    response_list = [
        BodyType(
            body_id=body_type.body_id,
            body=body_type.body
        )for body_type in body_types
    ]
    return response_list


@router.get("/transmission_types", response_model=List[TransmissionType])
async def get_transmission_types(session: AsyncSession = Depends(get_session)):
    query = select(TransmissionTypeOrm)
    results = await session.execute(query)
    transmission_types = results.scalars().all()
    response_list = [
        TransmissionType(
            transmission_type_id=transmission_type.transmission_type_id,
            transmission=transmission_type.transmission
        )for transmission_type in transmission_types
    ]
    return response_list


@router.get("/engine_types", response_model=List[EngineType])
async def get_engine_types(session: AsyncSession = Depends(get_session)):
    query = select(EngineTypeOrm)
    results = await session.execute(query)
    engine_types = results.scalars().all()
    response_list = [
        EngineType(
            engine_type_id=engine_type.engine_type_id,
            engine=engine_type.engine
        )for engine_type in engine_types
    ]
    return response_list