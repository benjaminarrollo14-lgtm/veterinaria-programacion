from pydantic import Field
from sqlmodel import SQLModel

from app.core.types import IdBody
from app.modules.duenios.schemas import DuenioResumen


class MascotaCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    especie: str = Field(min_length=1, max_length=50)
    duenio_id: IdBody  # agregación: viaja el id de un dueño que ya existe


class MascotaRead(SQLModel):
    id: int
    nombre: str
    especie: str
    duenio_id: int


class MascotaDetalleRead(MascotaRead):
    duenio: DuenioResumen
