from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_injector import attach_injector
from injector import Injector

from api.health.router import router as health_router

from api.modules import create_modules


def create_app(modules=None) -> FastAPI:
    if not modules:
        modules = create_modules()

    app = FastAPI()

    injector = Injector(modules)
    attach_injector(app, injector)

    app.include_router(health_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
