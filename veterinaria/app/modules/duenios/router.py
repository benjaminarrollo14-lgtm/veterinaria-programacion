from fastapi import APIRouter, Depends, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.types import IdPath
from app.modules.duenios import service
from app.modules.duenios.schemas import (
    DuenioCreate,
    DuenioRead,
    DuenioUpdate,
    FichaCreate,
    FichaRead,
)
from app.modules.mascotas.schemas import MascotaRead

router = APIRouter(prefix="/duenios", tags=["dueños"])


@router.post("/", response_model=DuenioRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: DuenioCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_duenio(session, datos)


@router.get("/{duenio_id}", response_model=DuenioRead)
async def obtener(duenio_id: IdPath, session: AsyncSession = Depends(get_session)):
    return await service.obtener_duenio(session, duenio_id)


@router.patch("/{duenio_id}", response_model=DuenioRead)
async def actualizar(
    duenio_id: IdPath,
    datos: DuenioUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await service.actualizar_duenio(session, duenio_id, datos)


@router.delete("/{duenio_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar(duenio_id: IdPath, session: AsyncSession = Depends(get_session)):
    await service.borrar_duenio(session, duenio_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{duenio_id}/ficha", response_model=FichaRead, status_code=status.HTTP_201_CREATED
)
async def crear_ficha(
    duenio_id: IdPath,
    datos: FichaCreate,
    session: AsyncSession = Depends(get_session),
):
    return await service.crear_ficha(session, duenio_id, datos)


@router.get("/{duenio_id}/mascotas", response_model=list[MascotaRead])
async def listar_mascotas(
    duenio_id: IdPath, session: AsyncSession = Depends(get_session)
):
    return await service.listar_mascotas_de_duenio(session, duenio_id)
