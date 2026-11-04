"""Deja la base en un estado conocido.

Crea las tablas que falten y (re)carga un conjunto de datos iniciales
determinista, por lo que ejecutar el script varias veces deja siempre la
misma base.

Uso:  python reiniciar.py

Estado conocido:
  * dos dueños, uno con ficha;
  * tres mascotas;
  * cuatro prácticas;
  * un turno con dos prácticas.
"""

import asyncio
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import delete
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

import app.models  # noqa: F401  (registra los modelos de tabla)
from app.core.config import get_settings
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.models import Duenio, FichaDuenio, Mascota, Practica, Turno, TurnoPractica


async def _limpiar_datos(session: AsyncSession) -> None:
    """Borra los datos en orden inverso a las dependencias de clave foránea."""
    await session.execute(delete(TurnoPractica))
    await session.execute(delete(Turno))
    await session.execute(delete(Mascota))
    await session.execute(delete(FichaDuenio))
    await session.execute(delete(Practica))
    await session.execute(delete(Duenio))


async def _sembrar_datos(session: AsyncSession) -> None:
    # Dos dueños; sólo el primero tiene ficha.
    dueno_juan = Duenio(nombre="Juan Pérez", email="juan.perez@example.com")
    dueno_maria = Duenio(nombre="María Gómez", email="maria.gomez@example.com")
    session.add_all([dueno_juan, dueno_maria])
    await session.flush()  # para obtener los ids generados

    # Ficha sólo para Juan.
    session.add(
        FichaDuenio(
            duenio_id=dueno_juan.id,
            telefono="+54 9 11 1234-5678",
            direccion="Calle Falsa 123",
        )
    )

    # Tres mascotas.
    mascota_fido = Mascota(nombre="Fido", especie="Perro", duenio_id=dueno_juan.id)
    session.add_all(
        [
            mascota_fido,
            Mascota(nombre="Mishi", especie="Gato", duenio_id=dueno_maria.id),
            Mascota(nombre="Max", especie="Perro", duenio_id=dueno_maria.id),
        ]
    )

    # Cuatro prácticas.
    practicas = [
        Practica(nombre="Consulta general", precio=Decimal("15000.00")),
        Practica(nombre="Vacuna", precio=Decimal("25000.00")),
        Practica(nombre="Desparasitación", precio=Decimal("12000.00")),
        Practica(nombre="Corte de uñas", precio=Decimal("8000.00")),
    ]
    session.add_all(practicas)
    await session.flush()  # para que las prácticas tengan id

    # Un turno con dos prácticas (Consulta general + Vacuna).
    turno = Turno(
        fecha=datetime(2026, 11, 5, 10, 30, tzinfo=timezone.utc),
        motivo="Control anual",
        mascota_id=mascota_fido.id,
    )
    session.add(turno)
    await session.flush()  # asigna turno.id

    # Crear explícitamente las filas de turno_practica con el precio copiado
    # del catálogo (RN-06), ya que la columna precio_unitario es NOT NULL.
    session.add_all(
        [
            TurnoPractica(
                turno_id=turno.id,
                practica_id=practicas[0].id,
                precio_unitario=practicas[0].precio,
            ),
            TurnoPractica(
                turno_id=turno.id,
                practica_id=practicas[1].id,
                precio_unitario=practicas[1].precio,
            ),
        ]
    )

    await session.commit()


async def main() -> None:
    engine = crear_motor(get_settings().database_url)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        async with crear_fabrica_sesiones(engine)() as session:
            await _limpiar_datos(session)
            await _sembrar_datos(session)
    finally:
        await engine.dispose()
    print(
        "Base dejada en estado conocido: 2 dueños (1 con ficha), "
        "3 mascotas, 4 prácticas y 1 turno con 2 prácticas."
    )


if __name__ == "__main__":
    asyncio.run(main())
