import unittest
from typing import TYPE_CHECKING, cast
from unittest.mock import patch

from givenpy import given, then, when
from hamcrest import assert_that, equal_to, instance_of, not_none, has_key

from api.chat.models import ChatRequest
from tests.infrastructure.steps import prepare_api_server
from tests.chat.steps import (
    prepare_mock_chat_dependencies,
    prepare_initialized_vector_store,
    prepare_empty_vector_store,
    prepare_successful_llm_response,
    prepare_empty_llm_response,
    prepare_failing_llm,
    prepare_vector_search_results,
    prepare_pricing_llm_response,
    set_mock_objects,
)

if TYPE_CHECKING:
    from fastapi.testclient import TestClient


class TestChatPipeline(unittest.TestCase):
    @patch("api.chat.chat_service.OpenAiLlmWrapper")
    @patch("api.chat.chat_service.VectorStore")
    @patch("api.chat.chat_service.RawDataPreprocessor")
    def test_chat_endpoint_pipeline_returns_valid_response(self, mock_preprocessor, mock_vector_store, mock_llm):
        with given(
            [
                prepare_api_server(),
                set_mock_objects(mock_preprocessor, mock_vector_store, mock_llm),
                prepare_mock_chat_dependencies(),
                prepare_initialized_vector_store(),
                prepare_successful_llm_response(),
            ]
        ) as context:
            client = cast("TestClient", context.client)

            # Set up vector store search results
            context.mock_vector_store_instance.similarity_search.return_value = [
                context.mock_preprocessor_instance.process_json_file.return_value[0]
            ]

            chat_request = ChatRequest(question="How do I integrate Oxylabs proxies?")

        with when():
            response = client.post("/chat/", json=chat_request.model_dump())

        with then():
            assert_that(response.status_code, equal_to(200))
            response_data = response.json()
            assert_that(response_data, has_key("answer"))
            assert_that(response_data, has_key("sources"))
            assert_that(response_data["answer"], not_none())
            assert_that(response_data["sources"], instance_of(list))

    @patch("api.chat.chat_service.OpenAiLlmWrapper")
    @patch("api.chat.chat_service.VectorStore")
    @patch("api.chat.chat_service.RawDataPreprocessor")
    def test_chat_endpoint_with_empty_vector_store_still_processes_request(
        self, mock_preprocessor, mock_vector_store, mock_llm
    ):
        with given(
            [
                prepare_api_server(),
                set_mock_objects(mock_preprocessor, mock_vector_store, mock_llm),
                prepare_mock_chat_dependencies(),
                prepare_empty_vector_store(),
                prepare_empty_llm_response(),
            ]
        ) as context:
            client = cast("TestClient", context.client)

            # Set up empty search results
            context.mock_vector_store_instance.similarity_search.return_value = []

            chat_request = ChatRequest(question="How do I use proxies?")

        with when():
            response = client.post("/chat/", json=chat_request.model_dump())

        with then():
            assert_that(response.status_code, equal_to(200))
            response_data = response.json()
            assert_that(response_data, has_key("answer"))
            assert_that(response_data, has_key("sources"))
            assert_that(len(response_data["sources"]), equal_to(0))

    def test_chat_endpoint_with_invalid_request_returns_400(self):
        with given([prepare_api_server()]) as context:
            client = cast("TestClient", context.client)

            invalid_request = {"invalid_field": "test"}

        with when():
            response = client.post("/chat/", json=invalid_request)

        with then():
            assert_that(response.status_code, equal_to(422))  # Validation error

    @patch("api.chat.chat_service.OpenAiLlmWrapper")
    @patch("api.chat.chat_service.VectorStore")
    @patch("api.chat.chat_service.RawDataPreprocessor")
    def test_chat_endpoint_handles_llm_error_gracefully(self, mock_preprocessor, mock_vector_store, mock_llm):
        with given(
            [
                prepare_api_server(),
                set_mock_objects(mock_preprocessor, mock_vector_store, mock_llm),
                prepare_mock_chat_dependencies(),
                prepare_initialized_vector_store(),
                prepare_failing_llm(),
            ]
        ) as context:
            client = cast("TestClient", context.client)

            # Set up empty search results for this test
            context.mock_vector_store_instance.similarity_search.return_value = []

            chat_request = ChatRequest(question="Test question")

        with when():
            response = client.post("/chat/", json=chat_request.model_dump())

        with then():
            assert_that(response.status_code, equal_to(500))
            response_data = response.json()
            assert_that(response_data, has_key("detail"))
            assert_that(response_data["detail"], equal_to("Internal server error"))

    @patch("api.chat.chat_service.OpenAiLlmWrapper")
    @patch("api.chat.chat_service.VectorStore")
    @patch("api.chat.chat_service.RawDataPreprocessor")
    def test_chat_pipeline_vector_search_integration(self, mock_preprocessor, mock_vector_store, mock_llm):
        with given(
            [
                prepare_api_server(),
                set_mock_objects(mock_preprocessor, mock_vector_store, mock_llm),
                prepare_mock_chat_dependencies(),
                prepare_initialized_vector_store(),
                prepare_vector_search_results(),
                prepare_pricing_llm_response(),
            ]
        ) as context:
            client = cast("TestClient", context.client)

            chat_request = ChatRequest(question="What are the pricing options for residential proxies?")

        with when():
            response = client.post("/chat/", json=chat_request.model_dump())

        with then():
            assert_that(response.status_code, equal_to(200))

            # Verify vector store was called (it gets called twice - once during warmup and once for actual request)
            call_args_list = context.mock_vector_store_instance.similarity_search.call_args_list
            # Check that our specific query was called
            actual_chat_call = any(
                call.args[0] == "What are the pricing options for residential proxies?" and call.kwargs.get("k") == 3
                for call in call_args_list
            )
            assert_that(actual_chat_call, equal_to(True))
            assert_that(context.mock_llm_instance.ask_structured.called, equal_to(True))

            response_data = response.json()
            assert_that(
                response_data["sources"], equal_to(["https://oxylabs.io/pricing", "https://developers.oxylabs.io/api"])
            )
