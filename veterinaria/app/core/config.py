"""Lectura de la configuración desde el entorno (archivo .env)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    database_url: str
    echo_sql: bool = False


def get_settings() -> Settings:
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "Falta la variable de entorno DATABASE_URL. "
            "Copiá env.example como .env y completala."
        )
    echo = os.getenv("ECHO_SQL", "false").strip().lower() in {"1", "true", "yes", "si"}
    return Settings(database_url=url, echo_sql=echo)
