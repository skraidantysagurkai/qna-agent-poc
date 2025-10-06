from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    api_version: str = Field(
        default="v1",
        description="Current API version",
    )

    build: Literal["dev", "test", "prod"] = Field(
        default="dev",
        description="Current runtime environment",
    )

    openai_api_key: str = Field(
        description="API key for OpenAI",
    )
