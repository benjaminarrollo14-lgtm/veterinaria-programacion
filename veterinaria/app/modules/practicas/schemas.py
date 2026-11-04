from decimal import Decimal

from pydantic import Field
from sqlmodel import SQLModel


class PracticaCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    # RN-04: validado acá (422) y también por el CHECK de la base.
    precio: Decimal = Field(gt=0, max_digits=10, decimal_places=2)


class PracticaRead(SQLModel):
    id: int
    nombre: str
    precio: Decimal
