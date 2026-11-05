from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota
    from app.modules.practicas.models import Practica


class TurnoPractica(SQLModel, table=True):
    """Tabla intermedia entre turnos y prácticas (composición muchos a muchos con datos).

    Guarda el precio_unitario congelado al reservar el turno (RN-06).
    Clave primaria compuesta (turno_id, practica_id) que garantiza que una
    misma práctica no figure dos veces en un turno (RN-07).
    turno_id lleva ON DELETE CASCADE: al borrar el turno, sus prácticas se borran con él (RN-09).
    """

    __tablename__ = "turno_practica"
    __table_args__ = (
        CheckConstraint(
            "precio_unitario > 0", name="ck_turno_practica_precio_unitario_positivo"
        ),
    )

    turno_id: int = Field(foreign_key="turno.id", ondelete="CASCADE", primary_key=True)
    practica_id: int = Field(
        foreign_key="practica.id",
        ondelete="RESTRICT",
        primary_key=True,
        index=True,  # índice en practica_id (esquema obligatorio)
    )
    # Precio copiado del catálogo al momento de crear el turno (RN-06, NUMERIC 10,2).
    precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)

    # Relaciones para navegación y carga anticipada (selectinload)
    turno: "Turno" = Relationship(back_populates="turno_practicas")
    practica: "Practica" = Relationship(back_populates="turno_practicas")


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
    # Total del turno (NUMERIC 12,2), calculado por el servidor (RN-06, RN-07).
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

    # Lado inverso de TurnoPractica.turno: permite selectinload del detalle.
    turno_practicas: list[TurnoPractica] = Relationship(
        back_populates="turno",
        sa_relationship_kwargs={"passive_deletes": True},
    )
