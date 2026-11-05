"""Importa todos los modelos de tabla para que queden registrados en
SQLModel.metadata y SQLAlchemy pueda resolver las relaciones entre
módulos."""

from app.modules.duenios.models import Duenio, FichaDuenio
from app.modules.mascotas.models import Mascota
from app.modules.practicas.models import Practica
from app.modules.turnos.models import Turno, TurnoPractica

__all__ = ["Duenio", "FichaDuenio", "Mascota", "Practica", "Turno", "TurnoPractica"]
