# app/main.py
from fastapi import FastAPI
from .routers import accounts
from .database import engine
from . import models
from prometheus_client import Counter, Histogram, generate_latest
from starlette.responses import Response

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Account Service API",
    description="API для управления счетами пользователей",
    version="1.0.0",
)

REQUEST_COUNT = Counter('request_count', 'Number of requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency', ['endpoint'])

@app.middleware("http")
async def add_prometheus_middleware(request, call_next):
    endpoint = request.url.path
    method = request.method
    REQUEST_COUNT.labels(method=method, endpoint=endpoint).inc()

    with REQUEST_LATENCY.labels(endpoint=endpoint).time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain")

app.include_router(accounts.router)
