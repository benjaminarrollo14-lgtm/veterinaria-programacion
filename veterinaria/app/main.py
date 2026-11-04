from contextlib import asynccontextmanager

from fastapi import FastAPI

import app.models  # noqa: F401  (registra los modelos de tabla)
from app.core.config import get_settings
from app.core.database import crear_fabrica_sesiones, crear_motor
from app.modules.duenios.router import router as duenios_router
from app.modules.health.router import router as health_router
from app.modules.mascotas.router import router as mascotas_router
from app.modules.practicas.router import router as practicas_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Arranque: el motor y la fábrica de sesiones se crean acá y viven en app.state.
    settings = get_settings()
    engine = crear_motor(settings.database_url, echo=settings.echo_sql)
    app.state.engine = engine
    app.state.session_factory = crear_fabrica_sesiones(engine)
    yield
    # Apagado: se cierra el motor (y con él el pool de conexiones).
    await engine.dispose()


app = FastAPI(title="Veterinaria", lifespan=lifespan)

app.include_router(health_router)
app.include_router(duenios_router)
app.include_router(mascotas_router)
app.include_router(practicas_router)
