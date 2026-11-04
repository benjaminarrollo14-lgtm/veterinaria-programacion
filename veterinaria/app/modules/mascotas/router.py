from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.types import IdPath, Page
from app.modules.mascotas import service
from app.modules.mascotas.schemas import MascotaCreate, MascotaDetalleRead, MascotaRead

router = APIRouter(prefix="/mascotas", tags=["mascotas"])


@router.post("/", response_model=MascotaRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: MascotaCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_mascota(session, datos)


@router.get("/", response_model=Page[MascotaRead])
async def listar(
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 20,
    session: AsyncSession = Depends(get_session),
):
    return await service.listar_mascotas(session, page, size)


@router.get("/{mascota_id}", response_model=MascotaDetalleRead)
async def obtener(mascota_id: IdPath, session: AsyncSession = Depends(get_session)):
    return await service.obtener_mascota(session, mascota_id)
