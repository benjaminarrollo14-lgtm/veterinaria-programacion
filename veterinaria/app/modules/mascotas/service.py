import math

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errors import conflicto
from app.core.types import Page
from app.modules.mascotas.models import Mascota
from app.modules.mascotas.schemas import MascotaCreate, MascotaRead

MENSAJES_MASCOTA = {
    "mascota_duenio_id_fkey": "El dueño indicado no existe.",
}


async def crear_mascota(session: AsyncSession, datos: MascotaCreate) -> Mascota:
    mascota = Mascota.model_validate(datos)
    session.add(mascota)
    try:
        await session.commit()
    except IntegrityError as exc:  # FK a duenio: el dueño no existe
        await session.rollback()
        raise conflicto(exc, MENSAJES_MASCOTA, "No se pudo crear la mascota.") from exc
    return mascota


async def obtener_mascota(session: AsyncSession, mascota_id: int) -> Mascota:
    """Mascota con su dueño en una sola consulta (joinedload: relación «a uno»)."""
    consulta = (
        select(Mascota)
        .where(Mascota.id == mascota_id)
        .options(joinedload(Mascota.duenio))
    )
    mascota = (await session.exec(consulta)).first()
    if mascota is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Mascota no encontrada.")
    return mascota


async def listar_mascotas(
    session: AsyncSession, page: int, size: int
) -> Page[MascotaRead]:
    total = (await session.exec(select(func.count()).select_from(Mascota))).one()
    pages = math.ceil(total / size)
    # La primera página siempre responde (aunque no haya resultados);
    # una página más allá de `pages` es un 422.
    if page > max(pages, 1):
        raise HTTPException(
            422,
            f"La página {page} no existe: hay {pages} página(s).",
        )
    consulta = (
        select(Mascota).order_by(Mascota.id).offset((page - 1) * size).limit(size)
    )
    filas = (await session.exec(consulta)).all()
    return Page[MascotaRead](
        items=[MascotaRead.model_validate(m) for m in filas],
        total=total,
        page=page,
        size=size,
        pages=pages,
    )
