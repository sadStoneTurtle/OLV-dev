"""RAG configuration models"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, ClassVar

from .i18n import I18nMixin, Description


class SimpleRAGConfig(I18nMixin, BaseModel):
    """Configuration for SimpleRAG (in-memory sentence-transformers based)"""

    model_name: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="Name of the sentence-transformers model to use for embeddings",
    )
    device: str = Field(
        default="cpu",
        description="Device to run the model on (cpu, cuda, mps)",
    )
    top_k: int = Field(
        default=3,
        description="Default number of documents to retrieve",
    )
    min_score: float = Field(
        default=0.3,
        description="Minimum similarity score for retrieved documents",
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "model_name": Description(
            en="Sentence-transformers model for embeddings",
            zh="用于嵌入的句子转换器模型",
        ),
        "device": Description(
            en="Device to run the model on (cpu, cuda, mps)",
            zh="运行模型的设备 (cpu, cuda, mps)",
        ),
        "top_k": Description(
            en="Number of documents to retrieve by default",
            zh="默认检索的文档数量",
        ),
        "min_score": Description(
            en="Minimum similarity score threshold",
            zh="最小相似度分数阈值",
        ),
    }


class RAGConfig(I18nMixin, BaseModel):
    """Main RAG configuration"""

    enabled: bool = Field(
        default=False,
        description="Enable or disable RAG functionality",
    )
    rag_type: str = Field(
        default="simple",
        description="Type of RAG engine to use (simple, chroma, faiss, etc.)",
    )
    simple: SimpleRAGConfig = Field(
        default_factory=SimpleRAGConfig,
        description="Configuration for SimpleRAG engine",
    )
    include_in_prompt: bool = Field(
        default=True,
        description="Whether to include RAG context in the prompt",
    )
    max_context_docs: Optional[int] = Field(
        default=3,
        description="Maximum number of documents to include in context (None for all)",
    )

    DESCRIPTIONS: ClassVar[Dict[str, Description]] = {
        "enabled": Description(
            en="Enable RAG (Retrieval-Augmented Generation)",
            zh="启用 RAG (检索增强生成)",
        ),
        "rag_type": Description(
            en="Type of RAG engine (simple, chroma, faiss)",
            zh="RAG 引擎类型 (simple, chroma, faiss)",
        ),
        "simple": Description(
            en="SimpleRAG configuration",
            zh="SimpleRAG 配置",
        ),
        "include_in_prompt": Description(
            en="Include retrieved context in the prompt",
            zh="在提示中包含检索到的上下文",
        ),
        "max_context_docs": Description(
            en="Maximum documents to include in context",
            zh="上下文中包含的最大文档数",
        ),
    }

