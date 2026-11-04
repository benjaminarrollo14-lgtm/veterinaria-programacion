from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.modules.practicas.models import Practica, TurnoPractica

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota


class Turno(SQLModel, table=True):
    __tablename__ = "turno"
    __table_args__ = (
        CheckConstraint("total >= 0", name="ck_turno_total_no_negativo"),
    )

    id: int | None = Field(default=None, primary_key=True)
    # Fecha y hora del turno con zona horaria.
    fecha: datetime = Field()
    # Motivo del turno.
    motivo: str = Field(max_length=255)
    # Total del turno (NUMERIC 12,2), calculado por el servidor (RN-07).
    total: Decimal = Field(max_digits=12, decimal_places=2)

    # Asociación: la mascota existe por sí misma. RESTRICT impide borrar una
    # mascota que tenga turnos. Índice en mascota_id (esquema obligatorio).
    mascota_id: int = Field(foreign_key="mascota.id", ondelete="RESTRICT", index=True)
    mascota: "Mascota" = Relationship(back_populates="turnos")

    # Composición: las prácticas del turno nacen con él y se copian del catálogo.
    # passive_deletes=True: al borrar el turno, la base borra las filas de
    # turno_practica por ON DELETE CASCADE, no el ORM (sección 4.3).
    practicas: list["Practica"] = Relationship(
        link_model=TurnoPractica,
        sa_relationship_kwargs={
            "back_populates": "turnos",
            "passive_deletes": True,
        },
    )
