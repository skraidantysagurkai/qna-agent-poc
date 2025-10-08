from typing import List

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    answer: str = Field(
        ..., description="A concise and complete answer to the user's question, based only on the provided context."
    )
    sources: List[str] = Field(
        ...,
        description="A list of source URLs referenced in the answer. Only include those explicitly found in the context.",
    )
