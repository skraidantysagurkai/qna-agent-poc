from typing import Annotated

from fastapi import APIRouter, status
from fastapi_injector import Injected

from api.shared.configs import Configs

router = APIRouter(
    prefix="/health",
    tags=["health"],
)


@router.get(
    path="/",
    status_code=status.HTTP_200_OK,
)
async def health_check(settings: Annotated[Configs, Injected(Configs)]):
    return {
        "status": "OK",
        "version": settings.api_version,
    }
