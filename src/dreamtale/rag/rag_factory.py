"""Factory for creating RAG instances"""

from typing import Dict, Any
from loguru import logger

from .rag_interface import RAGInterface
from .naive_rag import NaiveRAG
from .faiss_rag import FaissRAG


class RAGFactory:
    """Factory class for creating RAG engine instances"""

    @staticmethod
    def get_rag_engine(rag_type: str, **kwargs) -> RAGInterface:
        """
        Create and return a RAG engine instance.

        Args:
            rag_type: Type of RAG engine to create ('simple', 'chroma', 'faiss', etc.)
            **kwargs: Configuration parameters for the RAG engine

        Returns:
            RAGInterface: Initialized RAG engine instance

        Raises:
            ValueError: If rag_type is not supported
        """
        rag_type_lower = rag_type.lower()

        if rag_type_lower == "simple":
            logger.info("Creating testRAG engine")
            return NaiveRAG(**kwargs)

        # Future implementations can be added here:
        elif rag_type_lower == "faiss":
            logger.info("Creating FaissRAG engine")
            return FaissRAG(**kwargs)
        else:
            raise ValueError(
                f"Unsupported RAG type: {rag_type}. Supported types: faiss"
            )

