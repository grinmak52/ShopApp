import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router as api_router
from clients.cart import cart_client
from clients.catalog import catalog_client
from database.core.config import settings
from database.orm.db_helper import db_helper
from messaging.broker import broker
from service.exceptions import BadRequestError, NotFoundError, ServiceUnavailableError

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    yield
    await broker.close()
    await cart_client.close()
    await catalog_client.close()
    await db_helper.dispose()


main_app = FastAPI(title="Order Service", lifespan=lifespan)
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


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)