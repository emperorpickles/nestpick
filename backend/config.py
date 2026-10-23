from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# On Railway a persistent volume is mounted at /data.
# Detect Railway via the RAILWAY_ENVIRONMENT env var (set automatically by Railway).
# Locally, store the DB next to this file (backend/house_dashboard.db).
_on_railway = os.environ.get("RAILWAY_ENVIRONMENT") is not None
_data_dir = Path("/data") if _on_railway else Path(__file__).parent
_default_db_url = f"sqlite+aiosqlite:///{_data_dir}/house_dashboard.db"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = _default_db_url
    walkscore_api_key: str = ""
    census_api_key: str = ""
    # Add your deployed domain to CORS_ORIGINS env var (as a JSON list) if needed.
    # In production the frontend is served by the backend (same origin), so CORS
    # only matters for local dev.
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://localhost:4173",
        "http://localhost:8000",
    ]


settings = Settings()
