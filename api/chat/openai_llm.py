from openai import AsyncOpenAI, BaseModel
from typing import Type

from api.shared.logger import get_logger

LOGGER = get_logger(__name__)


class OpenAiLlmWrapper:
    def __init__(self, api_key: str, model: str):
        self.system_message = None
        self.api_key = api_key
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model

    def set_system_message(self, system_message: str):
        self.system_message = system_message

    async def ask_structured(self, user_message: str, schema: Type[BaseModel]) -> Type[BaseModel]:
        try:
            completion = await self.client.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_message},
                    {"role": "user", "content": user_message},
                ],
                response_format=schema,
            )
            parsed = completion.choices[0].message.parsed
            return parsed
        except Exception as e:  # noqa: BLE001
            LOGGER.error(f"Error during ask_structured(): {e!s}")
            raise e
