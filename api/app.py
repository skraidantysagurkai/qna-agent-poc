from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_injector import attach_injector
from injector import Injector

from api.chat.chat_service import ChatService
from api.health.router import router as health_router
from api.chat.router import router as chat_router

from api.modules import create_modules


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ = app.state.injector.get(ChatService)
    yield


def create_app(modules=None) -> FastAPI:
    if not modules:
        modules = create_modules()

    app = FastAPI(lifespan=lifespan)

    injector = Injector(modules)
    attach_injector(app, injector)

    app.include_router(health_router)
    app.include_router(chat_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
