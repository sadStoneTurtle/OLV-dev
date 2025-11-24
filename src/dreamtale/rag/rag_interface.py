"""RAG (Retrieval-Augmented Generation) Interface"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class RAGDocument:
    """
    Represents a document in the RAG system.

    Attributes:
        content: The text content of the document
        metadata: Optional metadata about the document (source, timestamp, etc.)
        score: Optional relevance score from retrieval
    """

    content: str
    metadata: Optional[Dict[str, Any]] = None
    score: Optional[float] = None


@dataclass
class RAGContext:
    """
    Represents the retrieved context for RAG.

    Attributes:
        documents: List of retrieved documents
        query: The original query used for retrieval
        metadata: Optional metadata about the retrieval process
    """

    documents: List[RAGDocument]
    query: str
    metadata: Optional[Dict[str, Any]] = None

    def to_formatted_string(self, max_docs: Optional[int] = None) -> str:
        """
        Format the RAG context as a string for inclusion in prompts.

        Args:
            max_docs: Maximum number of documents to include (None for all)

        Returns:
            Formatted string representation of the context
        """
        if not self.documents:
            return ""

        docs_to_use = self.documents[:max_docs] if max_docs else self.documents
        formatted_parts = ["[Retrieved Context]"]

        for i, doc in enumerate(docs_to_use, 1):
            score_str = f" (relevance: {doc.score:.3f})" if doc.score else ""
            formatted_parts.append(f"\n--- Document {i}{score_str} ---")
            formatted_parts.append(doc.content)

        formatted_parts.append("\n[End of Retrieved Context]\n")
        return "\n".join(formatted_parts)


class RAGInterface(ABC):
    """Base interface for all RAG implementations"""

    @abstractmethod
    async def add_documents(
        self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents to the RAG index.

        Args:
            documents: List of document texts to add
            metadatas: Optional list of metadata dictionaries for each document
        """
        pass

    @abstractmethod
    async def retrieve(
        self, query: str, top_k: int = 3, **kwargs
    ) -> List[RAGDocument]:
        """
        Retrieve relevant documents for a query.

        Args:
            query: The query text to search for
            top_k: Number of top documents to retrieve
            **kwargs: Additional retrieval parameters

        Returns:
            List of retrieved RAGDocument objects
        """
        pass

    @abstractmethod
    async def clear_index(self) -> None:
        """Clear all documents from the RAG index."""
        pass

    @abstractmethod
    def get_index_size(self) -> int:
        """
        Get the number of documents in the index.

        Returns:
            Number of documents in the index
        """
        pass

