import asyncio
import uvicorn
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api import router as api_router
from database.core.config import settings
from database.orm import db_helper
from messaging.broker import broker
from messaging.consumers import start_consumers
from service.exceptions import ConflictError, NotFoundError
from workers.expiration import run_expiration_worker


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.connect()
    await start_consumers(broker)
    worker = asyncio.create_task(run_expiration_worker())
    yield
    worker.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await worker
    await broker.close()
    await db_helper.dispose()



main_app = FastAPI(lifespan=lifespan)
main_app.include_router(api_router)


@main_app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    return JSONResponse(status_code=404, content={"detail": f"{exc.entity} not found"})


@main_app.exception_handler(ConflictError)
async def conflict_handler(request: Request, exc: ConflictError):
    return JSONResponse(status_code=409, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )