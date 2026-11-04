from pydantic import EmailStr, Field, model_validator
from sqlmodel import SQLModel


class FichaCreate(SQLModel):
    telefono: str = Field(min_length=1, max_length=50)
    direccion: str = Field(min_length=1, max_length=255)


class FichaRead(SQLModel):
    id: int
    duenio_id: int
    telefono: str
    direccion: str


class DuenioCreate(SQLModel):
    nombre: str = Field(min_length=1, max_length=100)
    email: EmailStr = Field(max_length=255)


class DuenioUpdate(SQLModel):
    """PATCH: todos los campos son opcionales; sólo se aplican los enviados."""

    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = Field(default=None, max_length=255)

    @model_validator(mode="after")
    def sin_nulos_explicitos(self):
        # Omitir un campo es válido; enviarlo en null no: ambos columnas son NOT NULL.
        for campo in self.model_fields_set:
            if getattr(self, campo) is None:
                raise ValueError(f"'{campo}' no puede ser null")
        return self


class DuenioRead(SQLModel):
    id: int
    nombre: str
    email: str
    ficha: FichaRead | None = None


class DuenioResumen(SQLModel):
    """Datos del dueño para incrustar en otras respuestas (sin ficha)."""

    id: int
    nombre: str
    email: str
