"""Simple in-memory RAG implementation using sentence-transformers"""

from typing import List, Dict, Any, Optional
import numpy as np
from loguru import logger

from .rag_interface import RAGInterface, RAGDocument


class NaiveRAG(RAGInterface):
    """
    Simple in-memory RAG implementation using cosine similarity.
    
    This implementation uses sentence-transformers for embeddings and
    stores everything in memory. Suitable for small to medium datasets.
    """

    def __init__(
        self,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        device: str = "cpu",
        **kwargs  # Accept but ignore extra parameters like top_k, min_score
    ):
        """
        Initialize the NaiveRAG system.

        Args:
            embedding_model_name: Name of the sentence-transformers model to use
            device: Device to run the model on ('cpu', 'cuda', 'mps')
            **kwargs: Additional parameters (ignored for now, for future extensibility)
        """
        self.embedding_model_name = embedding_model_name
        self.device = device
        self.documents: List[str] = []
        self.metadatas: List[Dict[str, Any]] = []
        self.embeddings: Optional[np.ndarray] = None
        self.embedding_model = None

        logger.info(f"Initializing NaiveRAG with model: {embedding_model_name} on {device}")
        self._setup_embedding_model()

    def _setup_embedding_model(self) -> None:
        """Load the sentence-transformers model."""
        try:
            from sentence_transformers import SentenceTransformer

            self.embedding_model = SentenceTransformer(self.embedding_model_name, device=self.device)
            logger.info(f"set up sentence-transformers model: {self.embedding_model_name}")
        except ImportError:
            logger.error(
                "sentence-transformers not installed. Install with: uv add sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers model: {e}")
            raise

    async def add_documents(
        self, documents: List[str], metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> None:
        """
        Add documents to the RAG index.

        Args:
            documents: List of document texts to add
            metadatas: Optional list of metadata dictionaries for each document
        """
        if not documents:
            logger.warning("No documents provided to add_documents")
            return

        if metadatas and len(metadatas) != len(documents):
            raise ValueError(
                f"Number of metadatas ({len(metadatas)}) must match number of documents ({len(documents)})"
            )

        logger.info(f"Adding {len(documents)} documents to RAG index")

        # Generate embeddings for new documents
        new_embeddings = self.embedding_model.encode(
            documents, convert_to_numpy=True, show_progress_bar=False
        )

        # Add to storage
        self.documents.extend(documents)
        if metadatas:
            self.metadatas.extend(metadatas)
        else:
            self.metadatas.extend([{}] * len(documents))

        # Update embeddings matrix
        if self.embeddings is None:
            self.embeddings = new_embeddings
        else:
            self.embeddings = np.vstack([self.embeddings, new_embeddings])

        logger.info(
            f"added {len(documents)} documents. Total documents: {len(self.documents)}"
        )

    async def retrieve(
        self, query: str, top_k: int = 3, **kwargs
    ) -> List[RAGDocument]:
        """
        Retrieve relevant documents for a query using cosine similarity.

        Args:
            query: The query text to search for
            top_k: Number of top documents to retrieve
            **kwargs: Additional parameters (min_score, etc.)

        Returns:
            List of retrieved RAGDocument objects
        """
        if not self.documents or self.embeddings is None:
            logger.warning("No documents in RAG index, returning empty results")
            return []

        min_score = kwargs.get("min_score", 0.0)

        # Generate query embedding
        query_embedding = self.embedding_model.encode(
            [query], convert_to_numpy=True, show_progress_bar=False
        )[0]

        # Calculate cosine similarity
        similarities = self._cosine_similarity(query_embedding, self.embeddings)

        # Get top-k indices
        top_k = min(top_k, len(self.documents))
        top_indices = np.argsort(similarities)[::-1][:top_k]

        # Filter by minimum score and create RAGDocument objects
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            if score >= min_score:
                results.append(
                    RAGDocument(
                        content=self.documents[idx],
                        metadata=self.metadatas[idx],
                        score=score,
                    )
                )

        logger.debug(
            f"Retrieved {len(results)} documents for query: '{query[:50]}...'"
        )
        return results

    def _cosine_similarity(
        self, query_embedding: np.ndarray, doc_embeddings: np.ndarray
    ) -> np.ndarray:
        """
        Calculate cosine similarity between query and document embeddings.

        Args:
            query_embedding: Query embedding vector
            doc_embeddings: Matrix of document embeddings

        Returns:
            Array of similarity scores
        """
        # Normalize vectors
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        doc_norms = doc_embeddings / np.linalg.norm(
            doc_embeddings, axis=1, keepdims=True
        )

        # Calculate cosine similarity
        similarities = np.dot(doc_norms, query_norm)
        return similarities

    async def clear_index(self) -> None:
        """Clear all documents from the RAG index."""
        self.documents = []
        self.metadatas = []
        self.embeddings = None
        logger.info("cleared RAG index")

    def get_index_size(self) -> int:
        """
        Get the number of documents in the index.

        Returns:
            Number of documents in the index
        """
        return len(self.documents)

