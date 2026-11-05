from datetime import datetime
from decimal import Decimal

from pydantic import Field
from sqlmodel import SQLModel

from app.core.types import IdBody


class TurnoPracticaCreate(SQLModel):
    """Práctica que se agrega al turno. Solo viaja el id de la práctica;
    el precio_unitario se copia del catálogo en el servidor (RN-06)."""

    practica_id: IdBody


class TurnoCreate(SQLModel):
    mascota_id: IdBody
    fecha: datetime
    motivo: str = Field(min_length=1, max_length=255)
    # Composición: las prácticas nacen con el turno; viajan sus ids (RN-05).
    practicas: list[TurnoPracticaCreate] = Field(min_length=1)


class MascotaResumen(SQLModel):
    """Datos de la mascota para incrustar en la respuesta del turno."""

    id: int
    nombre: str
    especie: str


class TurnoPracticaRead(SQLModel):
    practica_id: int
    nombre: str
    precio_unitario: Decimal


class TurnoRead(SQLModel):
    id: int
    fecha: datetime
    motivo: str
    # Total calculado por el servidor como suma de precios unitarios (RN-06, RN-07).
    total: Decimal
    mascota: MascotaResumen
    practicas: list[TurnoPracticaRead]
