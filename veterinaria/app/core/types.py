"""Tipos y envoltorios compartidos por los módulos."""

from typing import Annotated, Generic, TypeVar

from fastapi import Path
from pydantic import BaseModel, Field

# Un id de PostgreSQL INTEGER no puede pasar de este valor; si llegara uno
# mayor, asyncpg fallaría con un error 500 en lugar de un 422 claro.
MAX_INT4 = 2_147_483_647

# Id que viaja en un cuerpo (altas): positivo y dentro del rango de la base.
IdBody = Annotated[int, Field(ge=1, le=MAX_INT4)]

# Id que viaja en la ruta. Un id inexistente (0, negativo) es un 404, no un 422.
IdPath = Annotated[int, Path(le=MAX_INT4)]

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Envoltorio de listados paginados (sección 2.9)."""

    items: list[T]
    total: int
    page: int
    size: int
    pages: int
