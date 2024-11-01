from typing import Callable

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.routers import api_router
from app.config.settings import settings


def init_app() -> FastAPI:
    openapi_url = f"{settings.API}/openapi.json"
    application = FastAPI(
        title=f"🚀{settings.PROJECT_NAME}🚀",
        openapi_url=openapi_url,
        description=f"API docs for {settings.PROJECT_NAME}",
        version="1.0.0",
        contact={
            "name": "Bohdan Odintsov",
            "email": "odintsov.bogdan@gmail.com",
        },
    )

    register_middleware(application)
    application.include_router(api_router)
    application.add_event_handler("shutdown", on_shutdown_handler(application))
    return application


def on_shutdown_handler(application: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        pass
        # TODO call required functions on stop_app

    return stop_app


def register_middleware(application: FastAPI) -> None:
    if settings.CORS_ORIGIN_WHITELIST:
        application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Adjust as needed
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

app = init_app()
