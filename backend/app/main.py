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

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
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
