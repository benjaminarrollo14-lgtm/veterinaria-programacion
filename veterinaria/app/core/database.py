"""Motor, fábrica de sesiones y dependencia get_session.

El motor y la fábrica se crean en el lifespan de la aplicación (app/main.py)
y se guardan en app.state; acá sólo se declaran las funciones que los arman.
"""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


def crear_motor(database_url: str, echo: bool = False) -> AsyncEngine:
    return create_async_engine(database_url, echo=echo, pool_pre_ping=True)


def crear_fabrica_sesiones(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    # expire_on_commit=False: después del commit los objetos conservan sus
    # atributos y no hace falta volver a la base (que en async fallaría).
    return async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    """Una sesión por petición; se cierra sola al terminar."""
    fabrica: async_sessionmaker[AsyncSession] = request.app.state.session_factory
    async with fabrica() as session:
        yield session
