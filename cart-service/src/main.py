from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from api import router as api_router
from cache.redis import redis_client
from clients.catalog import catalog_client
from core.config import settings
from service.exceptions import BadRequestError, NotFoundError, ServiceUnavailableError


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await catalog_client.close()
    await redis_client.aclose()


main_app = FastAPI(title="Cart Service", lifespan=lifespan)
main_app.include_router(api_router)


@main_app.exception_handler(NotFoundError)
async def not_found(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": f"{exc.entity} not found"})


@main_app.exception_handler(BadRequestError)
async def bad_request(request: Request, exc: BadRequestError):
    return JSONResponse(status_code=400, content={"detail": exc.detail})


@main_app.exception_handler(ServiceUnavailableError)
async def unavailable(request: Request, exc: ServiceUnavailableError):
    return JSONResponse(status_code=503, content={"detail": exc.detail})


@main_app.exception_handler(RedisError)
async def redis_error(request: Request, exc: RedisError):
    return JSONResponse(status_code=503, content={"detail": "Cart storage is unavailable"})


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)