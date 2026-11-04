from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errors import conflicto
from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.duenios.schemas import DuenioCreate, DuenioUpdate, FichaCreate
from app.modules.mascotas.models import Mascota

MENSAJES_DUENIO = {
    "uq_duenio_email": "Ya existe un dueño con ese email.",
    "mascota_duenio_id_fkey": "No se puede borrar el dueño: tiene mascotas a su nombre.",
}
MENSAJES_FICHA = {
    "uq_ficha_duenio_duenio_id": "El dueño ya tiene una ficha.",
    "ficha_duenio_duenio_id_fkey": "El dueño indicado no existe.",
}


async def obtener_duenio(session: AsyncSession, duenio_id: int) -> Duenio:
    """Dueño con su ficha en una sola consulta (joinedload: relación «a uno»)."""
    consulta = (
        select(Duenio)
        .where(Duenio.id == duenio_id)
        .options(joinedload(Duenio.ficha))
        # Si el objeto ya está en la sesión (recién creado o modificado), esto
        # garantiza que `ficha` quede cargada y nunca se dispare una carga perezosa.
        .execution_options(populate_existing=True)
    )
    duenio = (await session.exec(consulta)).first()
    if duenio is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Dueño no encontrado.")
    return duenio


async def crear_duenio(session: AsyncSession, datos: DuenioCreate) -> Duenio:
    duenio = Duenio.model_validate(datos)
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflicto(exc, MENSAJES_DUENIO, "No se pudo crear el dueño.") from exc
    return await obtener_duenio(session, duenio.id)


async def actualizar_duenio(
    session: AsyncSession, duenio_id: int, datos: DuenioUpdate
) -> Duenio:
    duenio = await obtener_duenio(session, duenio_id)
    # exclude_unset: sólo los campos que el cliente envió (sección 2.6).
    duenio.sqlmodel_update(datos.model_dump(exclude_unset=True))
    session.add(duenio)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflicto(exc, MENSAJES_DUENIO, "No se pudo actualizar el dueño.") from exc
    return await obtener_duenio(session, duenio_id)


async def borrar_duenio(session: AsyncSession, duenio_id: int) -> None:
    duenio = await obtener_duenio(session, duenio_id)
    await session.delete(duenio)
    try:
        await session.commit()
    except IntegrityError as exc:  # ON DELETE RESTRICT de mascota.duenio_id (RN-08)
        await session.rollback()
        raise conflicto(
            exc, MENSAJES_DUENIO, "No se puede borrar el dueño: tiene mascotas a su nombre."
        ) from exc


async def crear_ficha(
    session: AsyncSession, duenio_id: int, datos: FichaCreate
) -> FichaDuenio:
    # El 404 es de un recurso de la ruta; las reglas (una sola ficha) las decide la base.
    await obtener_duenio(session, duenio_id)
    ficha = FichaDuenio(duenio_id=duenio_id, **datos.model_dump())
    session.add(ficha)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflicto(exc, MENSAJES_FICHA, "No se pudo crear la ficha.") from exc
    return ficha


async def listar_mascotas_de_duenio(
    session: AsyncSession, duenio_id: int
) -> list[Mascota]:
    await obtener_duenio(session, duenio_id)
    consulta = select(Mascota).where(Mascota.duenio_id == duenio_id).order_by(Mascota.id)
    return list((await session.exec(consulta)).all())
