from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.turnos.models import Turno


class TurnoPractica(SQLModel, table=True):
    """Tabla asociativa entre turnos y prácticas (relación muchos a muchos).

    La clave foránea a turno lleva ON DELETE CASCADE: al borrar un turno, la
    base borra automáticamente las filas de esta tabla. La relación
    Turno.practicas se declara con passive_deletes=True para que el ORM no
    intente vaciar ni borrar esas filas por su cuenta (sección 4.3).
    """

    __tablename__ = "turno_practica"
    turno_id: int = Field(foreign_key="turno.id", ondelete="CASCADE", primary_key=True)
    practica_id: int = Field(
        foreign_key="practica.id",
        ondelete="RESTRICT",
        primary_key=True,
        index=True,  # índice en practica_id (esquema obligatorio)
    )
    # Precio copiado del catálogo al momento de crear el turno (RN-06).
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)

    __table_args__ = (
        CheckConstraint(
            "precio_unitario > 0", name="ck_turno_practica_precio_unitario_positivo"
        ),
    )


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
