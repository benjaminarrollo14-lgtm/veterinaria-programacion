from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errors import conflicto
from app.modules.practicas.models import Practica
from app.modules.practicas.schemas import PracticaCreate

MENSAJES_PRACTICA = {
    "uq_practica_nombre": "Ya existe una práctica con ese nombre.",
    "ck_practica_precio_positivo": "El precio de la práctica debe ser mayor que cero.",
}


async def crear_practica(session: AsyncSession, datos: PracticaCreate) -> Practica:
    practica = Practica.model_validate(datos)
    session.add(practica)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflicto(exc, MENSAJES_PRACTICA, "No se pudo crear la práctica.") from exc
    # Releer el valor tal como lo guardó la base (NUMERIC(10,2) → "15000.00").
    await session.refresh(practica)
    return practica


async def listar_practicas(session: AsyncSession) -> list[Practica]:
    return list((await session.exec(select(Practica).order_by(Practica.id))).all())
