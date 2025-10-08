from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from api.shared.logger import get_logger
from paths import DATA_DIR

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.schema import Document
import re

LOGGER = get_logger(__name__)


class ContextEntry(BaseModel):
    section_name: str
    source_url: str
    content: str

    def format_entry(self) -> str:
        content = re.sub(r"<[^>]*>\s*\n", "", self.content)
        return f"### {self.section_name} <{self.source_url}>\n{content}\n\n"


class VectorStore:
    def __init__(
        self,
        openai_api_key: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        persist_directory: Optional[Path] = None,
    ):
        self.openai_api_key = openai_api_key
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        if persist_directory is None:
            self.persist_directory = DATA_DIR / "persistent_chroma_db"
        else:
            self.persist_directory = persist_directory

        self.persist_directory.mkdir(parents=True, exist_ok=True)
        LOGGER.info(f"Using persist directory: {self.persist_directory}")

        self._text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )

        self._embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self._vector_store = self._load_existing_store()

    def _load_existing_store(self) -> Optional[Chroma]:
        try:
            if self.persist_directory.exists() and list(self.persist_directory.glob("*")):
                _vector_store = Chroma(
                    persist_directory=str(self.persist_directory), embedding_function=self._embeddings
                )
                LOGGER.info("Loaded existing ChromaDB from disk")
                return _vector_store
            else:
                LOGGER.info("No existing ChromaDB found, will create new one")
                return None
        except Exception as e:
            LOGGER.warning(f"Failed to load existing ChromaDB: {e}. Will create new one.")
            return None

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        return self._text_splitter.split_documents(documents)

    @staticmethod
    def _create_documents_from_pairs(context_entries: List[ContextEntry]) -> List[Document]:
        documents = []

        for entry in context_entries:
            doc = Document(
                page_content=entry.content,
                metadata={"source_url": entry.source_url, "section_name": entry.section_name},
            )
            documents.append(doc)

        LOGGER.info(f"Created {len(documents)} documents from URL-content pairs")
        return documents

    def add_documents(self, documents: List[Document]) -> None:
        if not documents:
            LOGGER.warning("No documents to add to vector store")
            return

        split_docs = self._split_documents(documents)

        if self._vector_store is None:
            self._vector_store = Chroma.from_documents(
                documents=split_docs, embedding=self._embeddings, persist_directory=str(self.persist_directory)
            )
            LOGGER.info(f"Created new ChromaDB with {len(split_docs)} document chunks")
        else:
            self._vector_store.add_documents(split_docs)
            LOGGER.info(f"Added {len(split_docs)} document chunks to existing vector store")

    def add_from_preprocessed_data(self, context_entries: List[ContextEntry]) -> None:
        documents = self._create_documents_from_pairs(context_entries)
        self.add_documents(documents)

    def similarity_search(self, query: str, k: int = 4) -> List[ContextEntry]:
        if self._vector_store is None:
            LOGGER.warning("Vector store is empty. No documents to search.")
            return []

        results = [
            ContextEntry(
                section_name=entry.metadata["section_name"],
                source_url=entry.metadata["source_url"],
                content=entry.page_content,
            )
            for entry in self._vector_store.similarity_search(query, k=k)
        ]
        return results

    def is_vector_store_initialized(self) -> bool:
        return self._vector_store is not None

    def remove_persisted_store(self) -> None:
        if self.persist_directory.exists():
            for item in self.persist_directory.iterdir():
                if item.is_dir():
                    for subitem in item.iterdir():
                        subitem.unlink()
                    item.rmdir()
                else:
                    item.unlink()
            self.persist_directory.rmdir()
            LOGGER.info(f"Removed persisted vector store at {self.persist_directory}")
        else:
            LOGGER.info(f"No persisted vector store found at {self.persist_directory} to remove")
        self._vector_store = None
