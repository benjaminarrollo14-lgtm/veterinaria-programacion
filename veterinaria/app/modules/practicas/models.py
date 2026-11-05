from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from app.modules.turnos.models import TurnoPractica

if TYPE_CHECKING:
    from app.modules.turnos.models import Turno


class Practica(SQLModel, table=True):
    __tablename__ = "practica"
    __table_args__ = (
        UniqueConstraint("nombre", name="uq_practica_nombre"),  # RN-02
        CheckConstraint("precio > 0", name="ck_practica_precio_positivo"),  # RN-04
    )

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    # Dinero: Decimal (NUMERIC 10,2), nunca float.
    precio: Decimal = Field(max_digits=10, decimal_places=2)

    # Navegación al otro extremo de la relación turno_practica (muchos a muchos).
    turnos: list["Turno"] = Relationship(
        link_model=TurnoPractica,
        sa_relationship_kwargs={"back_populates": "practicas"},
    )

    # Lado inverso de TurnoPractica.practica (para selectinload del detalle).
    turno_practicas: list[TurnoPractica] = Relationship(
        back_populates="practica",
        sa_relationship_kwargs={"passive_deletes": True},
    )
