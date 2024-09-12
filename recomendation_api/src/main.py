import uvicorn
import sentry_sdk
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from contextlib import asynccontextmanager

from starlette.middleware.errors import ServerErrorMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from core import config

from api.v1 import recommendations
from services.auth import security_jwt
from middleware import LoggingMiddleware, BeforeRequest

settings = config.get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """@app.on_event("startup") and @app.on_event("shutdown") was deprecated.\n
    Recommended to use "lifespan"."""
    # start_up
    # await init_models()
    yield
    # await purge_pg_database()


app = FastAPI(
    title=settings.project_name,
    description='Сервис выдачи рекомендаций',
    version='1.0',
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
    dependencies=[Depends(security_jwt(required_roles=[]))]
)


sentry_sdk.init(
    dsn=settings.sentry_dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0,
)

app.add_middleware(BeforeRequest)
app.add_middleware(LoggingMiddleware)
app.add_middleware(ServerErrorMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


app.include_router(recommendations.router, prefix='/api/v1/recomm', tags=['recomendations'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host=settings.app_host,
        port=settings.app_port,
    )
