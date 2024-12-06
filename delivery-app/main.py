from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI

from api.api_v1.parcel import router as api_router, redis_helper
from core.config import settings
from core.rabbitmq import RabbitMQClient
from models import db_helper
from core.session_middleware import SessionMiddleware

rabbitmq_client = RabbitMQClient(amqp_url="amqp://guest:guest@localhost:5672/")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await rabbitmq_client.connect()
    await redis_helper.connect()
    app.state.redis_client = redis_helper.redis
    try:
        yield
    finally:
        await rabbitmq_client.close()
        await app.state.redis_client.close()
        await app.state.redis_client.wait_closed()
        await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)
main_app.add_middleware(SessionMiddleware)
main_app.include_router(
    api_router,
    prefix=settings.api_prefix.prefix,
)

if __name__ == "__main__":
    uvicorn.run(
        "delivery-app.main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
