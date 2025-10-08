import unittest
from typing import List
from unittest.mock import patch, MagicMock

from api.vector.store import VectorStore, ContextEntry
from langchain.schema import Document

from givenpy import given, when, then
from hamcrest import assert_that, instance_of, has_length, equal_to, not_none, is_
from tests.vector.steps import prepare_mock_vector_store, prepare_sample_context_entries


class TestVectorStore(unittest.TestCase):
    @patch("api.vector.store.Chroma")
    def test_when_documents_are_added_then_vector_store_is_created(self, mock_chroma):
        with given([prepare_mock_vector_store(), prepare_sample_context_entries()]) as context:
            vector_store: VectorStore = context.vector_store
            sample_entries: List[ContextEntry] = context.sample_entries

            mock_chroma_instance = MagicMock()
            mock_chroma.from_documents.return_value = mock_chroma_instance

            vector_store.remove_persisted_store()  # Ensure a clean state

        with when():
            vector_store.add_from_preprocessed_data(sample_entries)

        with then():
            assert_that(mock_chroma.from_documents.called, is_(True))
            assert_that(vector_store._vector_store, not_none())

    @patch("api.vector.store.Chroma")
    def test_when_similarity_search_is_performed_then_relevant_entries_are_returned(self, mock_chroma):
        with given([prepare_mock_vector_store(), prepare_sample_context_entries()]) as context:
            vector_store: VectorStore = context.vector_store
            sample_entries: List[ContextEntry] = context.sample_entries

            mock_chroma_instance = MagicMock()
            mock_chroma.from_documents.return_value = mock_chroma_instance

            # Mock search results
            mock_search_results = [
                Document(
                    page_content="<Integration Guides>\nOxylabs proxies are compatible with many software platforms",
                    metadata={
                        "section_name": "Integration Guides",
                        "source_url": "https://developers.oxylabs.io/proxies/integration-guides",
                    },
                )
            ]
            mock_chroma_instance.similarity_search.return_value = mock_search_results

            vector_store.remove_persisted_store()  # Ensure a clean state
            vector_store.add_from_preprocessed_data(sample_entries)  # Add documents first

        with when():
            results = vector_store.similarity_search("proxy integration", k=2)

        with then():
            assert_that(results, instance_of(list))
            assert_that(results, has_length(1))
            assert_that(results[0], instance_of(ContextEntry))
            assert_that(results[0].section_name, equal_to("Integration Guides"))
            assert_that(mock_chroma_instance.similarity_search.called, is_(True))
