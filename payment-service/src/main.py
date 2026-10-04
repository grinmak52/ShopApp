import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router as api_router
from database.core.config import settings
from database.orm.db_helper import db_helper
from messaging.broker import broker
from messaging.consumers import start_consumers

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    await start_consumers(broker)
    yield
    await broker.close()
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)
main_app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:main_app", host=settings.run.host, port=settings.run.port, reload=True)