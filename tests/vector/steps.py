from unittest.mock import MagicMock

from api.vector.store import VectorStore, ContextEntry
from api.vector.text_preprocessor import RawDataPreprocessor
from paths import TEST_DATA_DIR


def prepare_mock_vector_store():
    def step(context):
        context.vector_store = VectorStore(
            openai_api_key="test-key", persist_directory=TEST_DATA_DIR / "test_persistent_chroma_db"
        )
        # Mock the OpenAI embeddings to avoid actual API calls
        context.vector_store.embeddings = MagicMock()
        context.vector_store.embeddings.embed_documents.return_value = [[0.1] * 1536 for _ in range(10)]
        context.vector_store.embeddings.embed_query.return_value = [0.1] * 1536

    return step


def prepare_sample_context_entries():
    def step(context):
        context.sample_entries = [
            ContextEntry(
                section_name="Integration Guides",
                source_url="https://developers.oxylabs.io/proxies/integration-guides",
                content="<Integration Guides>\nOxylabs proxies are compatible with many software platforms and tools, from operating systems to browser add-ons. Explore our step-by-step integration guides and learn how to set up your proxies.",
            ),
            ContextEntry(
                section_name="API Documentation",
                source_url="https://developers.oxylabs.io/api/documentation",
                content="<API Documentation>\nComprehensive API documentation for Oxylabs services. Learn how to authenticate, make requests, and handle responses effectively.",
            ),
            ContextEntry(
                section_name="Pricing Information",
                source_url="https://oxylabs.io/pricing",
                content="<Pricing Information>\nDetailed pricing information for all Oxylabs products and services. Compare plans and find the best option for your needs.",
            ),
        ]

    return step


def prepare_mock_raw_data_preprocessor():
    def step(context):
        context.preprocessor = RawDataPreprocessor()

    return step
