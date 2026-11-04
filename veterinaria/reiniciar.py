"""Crea las tablas que falten sin borrar tablas ni datos existentes.

Uso:  python reiniciar.py

(Los datos iniciales se agregan en el Ejercicio 3.)
"""

import asyncio

from sqlmodel import SQLModel

import app.models  # noqa: F401  (registra los modelos de tabla)
from app.core.config import get_settings
from app.core.database import crear_motor


async def main() -> None:
    engine = crear_motor(get_settings().database_url)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    finally:
        await engine.dispose()
    print("Tablas faltantes creadas (las tablas y datos existentes se conservaron).")


if __name__ == "__main__":
    asyncio.run(main())
