from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import (
    MascotaResumen,
    TurnoCreate,
    TurnoDetalleRead,
    TurnoPracticaRead,
    TurnoRead,
    to_detalle,
)

MENSAJES_TURNO = {
    "turno_practica_pkey": "Una misma práctica no puede aparecer dos veces en un turno.",
}


async def crear_turno(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    """Da de alta un turno con sus prácticas en una sola transacción.

    RN-05: las prácticas referenciadas deben existir en el catálogo.
    RN-06: el precio unitario se copia del catálogo al momento de crear el turno.
    RN-07: el total es la suma de los precios unitarios de las prácticas y se
    guarda en la tabla turno.

    Si alguna práctica no existe, no queda guardado nada: ni el turno ni
    ninguna de sus prácticas.
    """
    # 1. Validar que la mascota exista (agregación: viaja el id de una mascota ya existente).
    mascota = await session.get(Mascota, datos.mascota_id)
    if mascota is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La mascota indicada no existe.")

    # 2. Validar que no haya prácticas duplicadas (RN-07: PK compuesta de turno_practica).
    ids = [p.practica_id for p in datos.practicas]
    if len(set(ids)) != len(ids):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Una misma práctica no puede aparecer dos veces en un turno.",
        )

    # 3. Validar que todas las prácticas existan (composición: nacen con el turno).
    consulta = select(Practica).where(Practica.id.in_(ids))
    practicas_db = list((await session.exec(consulta)).all())
    if len(practicas_db) != len(ids):
        existentes = {p.id for p in practicas_db}
        faltantes = sorted(set(ids) - existentes)
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Prácticas no encontradas: {', '.join(map(str, faltantes))}.",
        )

    # 4. Calcular el total (RN-07) y crear el turno con sus prácticas en una sola transacción.
    total = sum((p.precio for p in practicas_db), Decimal("0"))

    turno = Turno(
        mascota_id=datos.mascota_id,
        fecha=datos.fecha,
        motivo=datos.motivo,
        total=total,
    )
    session.add(turno)
    await session.flush()  # asigna turno.id sin hacer commit aún

    practicas_read: list[TurnoPracticaRead] = []
    for practica in practicas_db:
        tp = TurnoPractica(
            turno_id=turno.id,
            practica_id=practica.id,
            precio_unitario=practica.precio,
        )
        session.add(tp)
        practicas_read.append(
            TurnoPracticaRead(
                practica_id=practica.id,
                nombre=practica.nombre,
                precio_unitario=practica.precio,
            )
        )

    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            MENSAJES_TURNO.get(
                "turno_practica_pkey",
                "Una misma práctica no puede aparecer dos veces en un turno.",
            ),
        ) from exc

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


async def obtener_turno(session: AsyncSession, turno_id: int) -> TurnoDetalleRead:
    """Detalle de turno con mascota (a uno) y prácticas (colección).

    Carga anticipada con número fijo de consultas (Ejercicio 5 · sin N+1):
      1. SELECT principal de turno con JOIN a mascota (joinedload, a uno)
      2. SELECT de turno_practica WHERE turno_id = ? (selectinload)
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
    tp_list = list(turno.turno_practicas)
    return to_detalle(turno, tp_list)


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
