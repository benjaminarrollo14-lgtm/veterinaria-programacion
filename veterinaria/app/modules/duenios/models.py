from typing import TYPE_CHECKING, Optional

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.mascotas.models import Mascota


class Duenio(SQLModel, table=True):
    __tablename__ = "duenio"
    __table_args__ = (UniqueConstraint("email", name="uq_duenio_email"),)  # RN-01

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    email: str = Field(max_length=255)

    # Uno a uno: la clave foránea vive en ficha_duenio (la ficha es la parte
    # opcional, y así la tabla duenio no tiene columnas nulas ni cíclicas).
    # passive_deletes + delete-orphan: si la ficha no está cargada, el borrado
    # lo resuelve el ON DELETE CASCADE de la base.
    ficha: Optional["FichaDuenio"] = Relationship(
        back_populates="duenio",
        sa_relationship_kwargs={
            "uselist": False,
            "cascade": "all, delete-orphan",
            "passive_deletes": True,
        },
    )

    # Agregación: las mascotas existen por sí mismas. "all" hace que el ORM no
    # intente anular duenio_id al borrar un dueño: decide la base (RESTRICT).
    mascotas: list["Mascota"] = Relationship(
        back_populates="duenio",
        sa_relationship_kwargs={"passive_deletes": "all"},
    )


class FichaDuenio(SQLModel, table=True):
    __tablename__ = "ficha_duenio"
    __table_args__ = (UniqueConstraint("duenio_id", name="uq_ficha_duenio_duenio_id"),)  # RN-03

    id: int | None = Field(default=None, primary_key=True)
    duenio_id: int = Field(foreign_key="duenio.id", ondelete="CASCADE")
    telefono: str = Field(max_length=50)
    direccion: str = Field(max_length=255)

    duenio: Duenio = Relationship(back_populates="ficha")
