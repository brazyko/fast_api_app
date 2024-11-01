import os
import pathlib
import secrets
import sys
from typing import List

import uuid
from environs import Env
from pydantic import BaseSettings as PydanticSettings
from slugify import slugify

env = Env()


class SettingsBase(PydanticSettings):
    ROOT_DIR: str = os.path.abspath(os.path.dirname("src"))
    STATIC_DIR: str = f"{pathlib.Path().resolve().parent.parent}/static"

    if env.bool("READ_ENV", default=True):
        env.read_env(f"{ROOT_DIR}/.env")

    # Base settings
    # --------------------------------------------------------------------------
    PROJECT_NAME: str = "Check"
    PROJECT_NAME_SLUG: str = slugify(PROJECT_NAME)
    SECRET_KEY: str = env.str("SECRET_KEY", secrets.token_urlsafe(32))
    ENV_LABEL: str = env.str("ENV_LABEL", "")

    CORS_ORIGIN_WHITELIST: List[str] = env.list("CORS_ORIGIN_WHITELIST", ["*"])

    # API settings
    # --------------------------------------------------------------------------
    API: str = "/api"
    BATCH_SIZE: int = env.int("BATCH_SIZE", 25)  # default limit of items
    DATABASE_ROWS_LIMIT: int = env.int("DATABASE_ROWS_LIMIT", 500)
    UNLIMITED_VALUE: int = sys.maxsize

    # AUTH
    # --------------------------------------------------------------------------
    DEBUG_SECRET_KEY: str = env.str("DEBUG_SECRET_KEY", uuid.uuid4().hex)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = env.int("ACCESS_TOKEN_EXPIRES_MINUTES", 180)
    REFRESH_TOKEN_EXPIRES_DAYS: int = env.int("REFRESH_TOKEN_EXPIRES_DAYS", 720)

    # DATABASE settings
    # --------------------------------------------------------------------------
    DB_HOST: str = env.str("DB_HOST")
    DB_PORT: int = env.int("DB_PORT")
    DB_USER: str = env.str("DB_USER")
    DB_PASSWORD: str = env.str("DB_PASSWORD")
    DB_NAME: str = env.str("DB_NAME")
    DB_DRIVER: str = env.str("DB_DRIVER", "postgresql+asyncpg")
    DB_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    DB_URL_SYNC: str = (
        f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    SHOW_SQL: bool = env.bool("SHOW_SQL", False)
    CONNECTIONS_POOL_MIN_SIZE: int = env.int("CONNECTIONS_POOL_MIN_SIZE", 5)
    CONNECTIONS_POOL_MAX_OVERFLOW: int = env.int("CONNECTIONS_POOL_MAX_OVERFLOW", 25)


class SettingsLocal(SettingsBase):
    pass


def _get_settings():
    settings_class = SettingsLocal  # type: ignore
    return settings_class()


settings = _get_settings()
