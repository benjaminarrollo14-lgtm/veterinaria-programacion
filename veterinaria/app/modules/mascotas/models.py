from sqlmodel import Field, Relationship, SQLModel

from app.modules.duenios.models import Duenio


class Mascota(SQLModel, table=True):
    __tablename__ = "mascota"

    id: int | None = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100)
    especie: str = Field(max_length=50)
    # Agregación: la FK va del lado «muchos» (la mascota). RESTRICT impide
    # borrar un dueño con mascotas (RN-08); el índice acelera "mascotas del dueño".
    duenio_id: int = Field(foreign_key="duenio.id", ondelete="RESTRICT", index=True)

    duenio: Duenio = Relationship(back_populates="mascotas")
