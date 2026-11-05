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
    # Composición: las prácticas nacen con el turno; viajan sus ids.
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
    # Total calculado por el servidor como suma de precios unitarios (RN-07).
    total: Decimal
    mascota: MascotaResumen
    practicas: list[TurnoPracticaRead]


class PracticaResumen(SQLModel):
    """Datos de la práctica para incrustar en la respuesta del detalle."""

    id: int
    nombre: str
    precio: Decimal


class TurnoPracticaResumen(SQLModel):
    """Fila de turno_practica para la respuesta del detalle (con su práctica)."""

    turno_id: int
    practica_id: int
    precio_unitario: Decimal
    practica: PracticaResumen


class TurnoDetalleRead(TurnoRead):
    """Detalle con prácticas cargadas vía TurnoPractica (para selectinload)."""

    practicas: list[TurnoPracticaResumen]


def to_detalle(turno: Turno, tp_list) -> TurnoDetalleRead:
    """Convierte un Turno (con mascota y prácticas precargadas) a DTO de detalle.

    tp_list: lista de TurnoPractica con su practica ya cargada vía selectinload.
    """
    from app.modules.turnos.models import TurnoPractica

    practicas = []
    for tp in tp_list:
        assert isinstance(tp, TurnoPractica)
        assert tp.practica is not None  # precargada con selectinload
        practicas.append(
            TurnoPracticaResumen(
                turno_id=tp.turno_id,
                practica_id=tp.practica_id,
                precio_unitario=tp.precio_unitario,
                practica=PracticaResumen(
                    id=tp.practica.id,
                    nombre=tp.practica.nombre,
                    precio=tp.practica.precio,
                ),
            )
        )
    return TurnoDetalleRead(
        id=turno.id,
        fecha=turno.fecha,
        motivo=turno.motivo,
        total=turno.total,
        mascota=MascotaResumen(
            id=turno.mascota.id,
            nombre=turno.mascota.nombre,
            especie=turno.mascota.especie,
        ),
        practicas=practicas,
    )
