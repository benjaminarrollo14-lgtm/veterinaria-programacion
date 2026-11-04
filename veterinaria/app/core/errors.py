"""Traducción de errores de la base a respuestas HTTP."""

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError


def nombre_restriccion(exc: IntegrityError) -> str | None:
    """Nombre de la restricción que violó la escritura, si el controlador lo informa."""
    causa = getattr(exc.orig, "__cause__", None)
    return getattr(causa, "constraint_name", None)


def conflicto(
    exc: IntegrityError, mensajes: dict[str, str], por_defecto: str
) -> HTTPException:
    """409 con un mensaje propio según la restricción violada."""
    nombre = nombre_restriccion(exc)
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail=mensajes.get(nombre or "", por_defecto),
    )
