from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.catalog import PRODUCTS
from app.config import settings
from app.database import init_db
from app.routers import payments


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Payments Service", version="1.0.0", lifespan=lifespan)

origins = (
    settings.cors_origins
    if isinstance(settings.cors_origins, list)
    else [settings.cors_origins]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(payments.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/products")
def products():
    return list(PRODUCTS.values())
