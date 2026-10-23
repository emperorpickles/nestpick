from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from config import settings
from database import init_db
from routers import comparison, neighborhood, properties, ratings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="House Dashboard", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(properties.router)
app.include_router(neighborhood.router)
app.include_router(comparison.router)
app.include_router(ratings.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


class SPAStaticFiles(StaticFiles):
    """Serve index.html for unknown paths so client-side routes survive a refresh."""

    async def get_response(self, path, scope):
        try:
            return await super().get_response(path, scope)
        except StarletteHTTPException as exc:
            # Real misses (API routes, missing asset files) should still 404.
            if exc.status_code != 404 or path.startswith("api/") or "." in path.rsplit("/", 1)[-1]:
                raise
            return await super().get_response("index.html", scope)


# Serve React build in production (Railway deployment)
# Resolve path relative to this file so it works regardless of cwd
_frontend_dist = Path(__file__).parent.parent / "frontend" / "dist"
try:
    app.mount("/", SPAStaticFiles(directory=str(_frontend_dist), html=True), name="static")
except RuntimeError:
    pass  # frontend not built yet (dev mode)
