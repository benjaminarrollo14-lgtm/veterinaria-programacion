from decimal import Decimal

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica
from app.modules.turnos.schemas import (
    MascotaResumen,
    TurnoCreate,
    TurnoPracticaRead,
    TurnoRead,
)


async def crear_turno(session: AsyncSession, datos: TurnoCreate) -> TurnoRead:
    """Da de alta un turno con sus prácticas en una sola transacción.

    RN-05: las prácticas referenciadas deben existir en el catálogo.
    RN-06: el precio unitario se copia del catálogo al momento de crear el turno.
    RN-07: el total es la suma de los precios unitarios de las prácticas.

    Si alguna práctica no existe, no queda guardado nada: ni el turno ni
    ninguna de sus prácticas.
    """
    # 1. Validar que la mascota exista (agregación: viaja el id de una mascota ya existente).
    mascota = await session.get(Mascota, datos.mascota_id)
    if mascota is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "La mascota indicada no existe.")

    # 2. Validar que todas las prácticas existan (composición: nacen con el turno).
    ids = [p.practica_id for p in datos.practicas]
    consulta = select(Practica).where(Practica.id.in_(ids))
    practicas_db = list((await session.exec(consulta)).all())
    if len(practicas_db) != len(ids):
        existentes = {p.id for p in practicas_db}
        faltantes = sorted(set(ids) - existentes)
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Prácticas no encontradas: {', '.join(map(str, faltantes))}.",
        )

    # 3. Crear el turno y sus prácticas en una sola transacción.
    turno = Turno(
        mascota_id=datos.mascota_id,
        fecha=datos.fecha,
        motivo=datos.motivo,
    )
    session.add(turno)
    await session.flush()  # asigna turno.id sin hacer commit aún

    total = Decimal("0")
    practicas_read: list[TurnoPracticaRead] = []
    for practica in practicas_db:
        tp = TurnoPractica(
            turno_id=turno.id,
            practica_id=practica.id,
            precio_unitario=practica.precio,
        )
        session.add(tp)
        total += practica.precio
        practicas_read.append(
            TurnoPracticaRead(
                practica_id=practica.id,
                nombre=practica.nombre,
                precio_unitario=practica.precio,
            )
        )

    await session.commit()

    return TurnoRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=total,
        mascota=MascotaResumen(
            id=mascota.id,
            nombre=mascota.nombre,
            especie=mascota.especie,
        ),
        practicas=practicas_read,
    )
