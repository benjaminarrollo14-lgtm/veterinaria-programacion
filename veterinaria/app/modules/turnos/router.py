from fastapi import APIRouter, Depends, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.database import get_session
from app.modules.turnos import service
from app.modules.turnos.schemas import TurnoCreate, TurnoRead

router = APIRouter(prefix="/turnos", tags=["turnos"])


@router.post("/", response_model=TurnoRead, status_code=status.HTTP_201_CREATED)
async def crear(datos: TurnoCreate, session: AsyncSession = Depends(get_session)):
    return await service.crear_turno(session, datos)
