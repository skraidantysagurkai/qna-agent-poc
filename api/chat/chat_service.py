import asyncio
from typing import List

from injector import singleton, inject

from api.chat.models import ChatResponse, ChatRequest
from api.chat.openai_llm import OpenAiLlmWrapper
from api.chat.prompt_builder import PromptBuilder
from api.shared.configs import Configs
from api.shared.logger import get_logger
from api.vector.store import VectorStore, ContextEntry
from api.vector.text_preprocessor import RawDataPreprocessor
from paths import ROOT_DIR, DATA_DIR, TEST_DATA_DIR

LOOGER = get_logger(__name__)


@inject
@singleton
class ChatService:
    def __init__(self, configs: Configs):
        self.configs = configs

        if configs.build == "test":
            persistent_vector_store_dir = TEST_DATA_DIR / "persistent_chroma_db"
        else:
            persistent_vector_store_dir = DATA_DIR / "persistent_chroma_db"

        self.vector_store = VectorStore(configs.openai_api_key, persist_directory=persistent_vector_store_dir)
        self.preprocessor = RawDataPreprocessor()
        self.llm_wrapper = OpenAiLlmWrapper(api_key=configs.openai_api_key, model=configs.openai_model)
        self.prompt_builder = PromptBuilder()

        self._start_up()
        asyncio.get_event_loop().create_task(self._warm_up_dependencies())

    def _start_up(self):
        if self.vector_store.is_vector_store_initialized():
            LOOGER.info("Vector store already initialized, skipping data loading.")
        else:
            LOOGER.info("Vector store not initialized, loading and processing data.")
            processed_data = self.preprocessor.process_json_file(ROOT_DIR / self.configs.scraped_data_path)
            self.vector_store.add_from_preprocessed_data(processed_data)

        self.llm_wrapper.set_system_message(self.prompt_builder.get_system_message())

    async def _warm_up_dependencies(self):
        LOOGER.info("Warming up dependencies...")
        query = "Proxy China"
        context_entries: List[ContextEntry] = self.vector_store.similarity_search(query, k=3)
        user_message = self.prompt_builder.build_user_message(query, context_entries)
        await self.llm_wrapper.ask_structured(user_message, ChatResponse)  # type: ignore[arg-type]

    async def chat(self, query: ChatRequest) -> ChatResponse:
        context_entries: List[ContextEntry] = self.vector_store.similarity_search(query.question, k=3)
        user_message = self.prompt_builder.build_user_message(query.question, context_entries)
        return await self.llm_wrapper.ask_structured(user_message, ChatResponse)  # type: ignore[arg-type]
