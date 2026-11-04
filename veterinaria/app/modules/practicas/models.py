from decimal import Decimal

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, SQLModel


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
