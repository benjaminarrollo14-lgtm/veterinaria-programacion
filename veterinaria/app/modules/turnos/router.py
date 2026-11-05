from fastapi import APIRouter, Depends, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.core.types import IdPath
from app.modules.turnos import service
from app.modules.turnos.schemas import TurnoCreate, TurnoDetalleRead, TurnoRead

router = APIRouter(prefix="/turnos", tags=["turnos"])


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: TurnoCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_turno(session, datos)


@router.get("/{turno_id}", response_model=TurnoDetalleRead)
async def obtener(turno_id: IdPath, session: AsyncSession = Depends(get_session)):
    # IdPath valida rango 1..MAX_INT4; fuera de eso FastAPI responde 422.
    return await service.obtener_turno(session, turno_id)


@router.delete("/{turno_id}", status_code=status.HTTP_204_NO_CONTENT)
async def borrar(turno_id: IdPath, session: AsyncSession = Depends(get_session)):
    await service.borrar_turno(session, turno_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: TurnoCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_turno(session, datos)
