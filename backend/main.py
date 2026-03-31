from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.services.notifier import delivery_worker
from backend.database import init_db
from backend.auth import seed_default_api_key, auth_router
from backend.routers.refresh import refresh_router
from backend.routers.products import products_router
from backend.routers.analytics import analytics_router
from backend.routers.notifications import notifications_router
import asyncio
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    seed_default_api_key()
    task = asyncio.create_task(delivery_worker())
    yield
    task.cancel()

app = FastAPI(title="PriceCatch API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(refresh_router, prefix="/api", tags=["refresh"])
app.include_router(products_router, prefix="/api", tags=["products"])
app.include_router(analytics_router, prefix="/api", tags=["analytics"])
app.include_router(notifications_router, prefix="/api", tags=["notifications"])
app.include_router(auth_router, prefix="/api", tags=["auth"])

os.makedirs("frontend/static", exist_ok=True)
app.mount("/", StaticFiles(directory="frontend", html=True), name="static")
