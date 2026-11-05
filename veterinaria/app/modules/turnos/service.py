from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.errors import conflicto
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import (
    MascotaResumen,
    TurnoCreate,
    TurnoPracticaRead,
    TurnoRead,
)

MENSAJES_TURNO = {
    "turno_practica_pkey": "Una misma práctica no puede aparecer dos veces en un turno.",
    "turno_mascota_id_fkey": "La mascota indicada no existe.",
    "turno_practica_practica_id_fkey": "Una o más prácticas indicadas no existen.",
}


async def crear_turno(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    """Da de alta un turno con sus prácticas en una sola transacción.

    RN-05: las prácticas referenciadas deben existir en el catálogo.
    RN-06: el precio unitario se copia del catálogo al momento de crear el turno.
    RN-07: el total es la suma de los precios unitarios de las prácticas y se
    guarda en la tabla turno.
    C-04: si la mascota o alguna práctica no existe, responde 409 y no queda guardado nada.
    """
    # 1. Validar que la mascota exista (asociación). Si no existe, 409 (C-04).
    mascota = await session.get(Mascota, datos.mascota_id)
    if mascota is None:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "La mascota indicada no existe.",
        )

    # 2. Validar que no haya prácticas duplicadas en el cuerpo (RN-07: PK compuesta).
    ids = [p.practica_id for p in datos.practicas]
    if len(set(ids)) != len(ids):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Una misma práctica no puede aparecer dos veces en un turno.",
        )

    # 3. Validar que todas las prácticas existan en el catálogo (RN-05, C-04).
    consulta = select(Practica).where(Practica.id.in_(ids))
    practicas_db = list((await session.exec(consulta)).all())
    if len(practicas_db) != len(set(ids)):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Una o más prácticas indicadas no existen.",
        )

    # Mapa para conservar orden y acceso rápido a datos del catálogo
    practicas_por_id = {p.id: p for p in practicas_db}

    # 4. Calcular el total (RN-06, RN-07)
    total = sum((practicas_por_id[pid].precio for pid in ids), Decimal("0"))

    turno = Turno(
        mascota_id=datos.mascota_id,
        fecha=datos.fecha,
        motivo=datos.motivo,
        total=total,
    )
    session.add(turno)
    await session.flush()  # asigna turno.id

    practicas_read: list[TurnoPracticaRead] = []
    for pid in ids:
        practica_catalogo = practicas_por_id[pid]
        tp = TurnoPractica(
            turno_id=turno.id,
            practica_id=pid,
            precio_unitario=practica_catalogo.precio,
        )
        session.add(tp)
        practicas_read.append(
            TurnoPracticaRead(
                practica_id=pid,
                nombre=practica_catalogo.nombre,
                precio_unitario=practica_catalogo.precio,
            )
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise conflicto(exc, MENSAJES_TURNO, "No se pudo crear el turno.") from exc

    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaResumen(
            id=mascota.id,
            nombre=mascota.nombre,
            especie=mascota.especie,
        ),
        practicas=practicas_read,
    )


async def obtener_turno(session: AsyncSession, turno_id: int) -> TurnoRead:
    """Detalle de turno con mascota (a uno) y prácticas (colección).

    Carga anticipada con número fijo de consultas (Ejercicio 5 · sin N+1):
      1. SELECT principal de turno con JOIN a mascota (joinedload, relación a uno)
      2. SELECT de turno_practica WHERE turno_id IN (?) (selectinload, colección)
      3. SELECT de practica WHERE id IN (...) (selectinload anidado)

    No depende de carga perezosa: en async fallaría con MissingGreenlet.
    """
    consulta = (
        select(Turno)
        .where(Turno.id == turno_id)
        .options(
            joinedload(Turno.mascota),
            selectinload(Turno.turno_practicas).selectinload(TurnoPractica.practica),
        )
    )
    turno = (await session.exec(consulta)).first()
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turno no encontrado.")

    practicas_read = [
        TurnoPracticaRead(
            practica_id=tp.practica_id,
            nombre=tp.practica.nombre,
            precio_unitario=tp.precio_unitario,
        )
        for tp in sorted(turno.turno_practicas, key=lambda x: x.practica_id)
    ]

    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaResumen(
            id=turno.mascota.id,
            nombre=turno.mascota.nombre,
            especie=turno.mascota.especie,
        ),
        practicas=practicas_read,
    )


async def borrar_turno(session: AsyncSession, turno_id: int) -> None:
    """Borra un turno. RN-09: ON DELETE CASCADE borra sus turno_practica en la base.

    404 si no existe. La relación Turno.practicas usa passive_deletes=True,
    así que el ORM no intenta borrar ni vaciar filas de turno_practica.
    """
    turno = await session.get(Turno, turno_id)
    if turno is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Turno no encontrado.")
    await session.delete(turno)
    await session.commit()
