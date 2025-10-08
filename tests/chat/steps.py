from unittest.mock import MagicMock, AsyncMock
from api.chat.models import ChatResponse
from api.vector.store import ContextEntry


def set_mock_objects(mock_preprocessor, mock_vector_store, mock_llm):
    def step(context):
        context.mock_preprocessor = mock_preprocessor
        context.mock_vector_store = mock_vector_store
        context.mock_llm = mock_llm

    return step


def prepare_mock_chat_dependencies():
    def step(context):
        if hasattr(context, "mock_preprocessor"):
            context.mock_preprocessor_instance = MagicMock()
            context.mock_preprocessor.return_value = context.mock_preprocessor_instance

        if hasattr(context, "mock_vector_store"):
            context.mock_vector_store_instance = MagicMock()
            context.mock_vector_store.return_value = context.mock_vector_store_instance

        if hasattr(context, "mock_llm"):
            context.mock_llm_instance = MagicMock()
            context.mock_llm.return_value = context.mock_llm_instance
            context.mock_llm_instance.set_system_message = MagicMock()

    return step


def prepare_initialized_vector_store():
    def step(context):
        if hasattr(context, "mock_vector_store_instance"):
            context.mock_vector_store_instance.is_vector_store_initialized.return_value = True
        if hasattr(context, "mock_preprocessor_instance"):
            context.mock_preprocessor_instance.process_json_file.return_value = [
                ContextEntry(
                    section_name="Integration Guides",
                    source_url="https://developers.oxylabs.io/proxies/integration-guides",
                    content="<Integration Guides>\nOxylabs proxies are compatible with many software platforms",
                )
            ]

    return step


def prepare_empty_vector_store():
    def step(context):
        if hasattr(context, "mock_vector_store_instance"):
            context.mock_vector_store_instance.is_vector_store_initialized.return_value = False
            context.mock_vector_store_instance.add_from_preprocessed_data = MagicMock()
        if hasattr(context, "mock_preprocessor_instance"):
            context.mock_preprocessor_instance.process_json_file.return_value = []

    return step


def prepare_successful_llm_response():
    def step(context):
        if hasattr(context, "mock_llm_instance"):
            context.mock_llm_instance.ask_structured = AsyncMock(
                return_value=ChatResponse(
                    answer="Oxylabs proxies are compatible with many software platforms and tools.",
                    sources=["https://developers.oxylabs.io/proxies/integration-guides"],
                )
            )

    return step


def prepare_empty_llm_response():
    def step(context):
        if hasattr(context, "mock_llm_instance"):
            context.mock_llm_instance.ask_structured = AsyncMock(
                return_value=ChatResponse(answer="I don't have specific information about that topic.", sources=[])
            )

    return step


def prepare_failing_llm():
    def step(context):
        if hasattr(context, "mock_llm_instance"):
            context.mock_llm_instance.ask_structured = AsyncMock(side_effect=Exception("LLM service unavailable"))

    return step


def prepare_vector_search_results():
    def step(context):
        if hasattr(context, "mock_vector_store_instance"):
            context.expected_context_entries = [
                ContextEntry(
                    section_name="Pricing Information",
                    source_url="https://oxylabs.io/pricing",
                    content="<Pricing Information>\nDetailed pricing for residential proxies",
                ),
                ContextEntry(
                    section_name="API Documentation",
                    source_url="https://developers.oxylabs.io/api",
                    content="<API Documentation>\nHow to use the API for proxy requests",
                ),
            ]
            context.mock_vector_store_instance.similarity_search.return_value = context.expected_context_entries

    return step


def prepare_pricing_llm_response():
    def step(context):
        if hasattr(context, "mock_llm_instance"):
            context.mock_llm_instance.ask_structured = AsyncMock(
                return_value=ChatResponse(
                    answer="Based on the pricing information and API documentation provided...",
                    sources=["https://oxylabs.io/pricing", "https://developers.oxylabs.io/api"],
                )
            )

    return step
