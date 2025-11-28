"""
RAG 사용 예제

이 스크립트는 RAG 기능을 독립적으로 테스트하는 방법을 보여줍니다.
"""

import asyncio
from loguru import logger

from .naive_rag import NaiveRAG


async def example_basic_usage():
    """기본 사용 예제"""
    logger.info("=== 기본 RAG 사용 예제 ===")

    # RAG 엔진 초기화
    rag = NaiveRAG(
        model_name="sentence-transformers/all-MiniLM-L6-v2", device="cpu"
    )

    # 문서 추가
    documents = [
        "Open-LLM-VTuber는 오픈소스 VTuber 프로젝트입니다. Python과 FastAPI로 구현되었습니다.",
        "이 프로젝트는 Live2D 모델을 지원하며 실시간으로 표정을 변경할 수 있습니다.",
        "ASR(음성 인식), TTS(음성 합성), LLM(대화 모델)을 통합하여 실시간 대화가 가능합니다.",
        "WebSocket을 사용하여 클라이언트와 서버 간 실시간 통신을 구현했습니다.",
        "다양한 LLM을 지원합니다: OpenAI, Claude, Ollama, llama.cpp 등",
    ]

    logger.info(f"Adding {len(documents)} documents...")
    await rag.add_documents(documents)
    logger.info(f"✅ Index size: {rag.get_index_size()} documents")

    # 검색 테스트
    queries = [
        "VTuber 프로젝트에 대해 알려줘",
        "어떤 LLM을 사용할 수 있나요?",
        "실시간 통신은 어떻게 구현했나요?",
    ]

    for query in queries:
        logger.info(f"\n🔍 Query: {query}")
        results = await rag.retrieve(query, top_k=2, min_score=0.2)

        if results:
            for i, doc in enumerate(results, 1):
                logger.info(f"  [{i}] Score: {doc.score:.3f}")
                logger.info(f"      Content: {doc.content[:100]}...")
        else:
            logger.warning("  No results found")


async def example_with_metadata():
    """메타데이터를 포함한 예제"""
    logger.info("\n=== 메타데이터 포함 예제 ===")

    rag = NaiveRAG(device="cpu")

    # 메타데이터와 함께 문서 추가
    documents = [
        "FastAPI는 Python 웹 프레임워크입니다.",
        "Pydantic은 데이터 검증 라이브러리입니다.",
        "Uvicorn은 ASGI 서버입니다.",
    ]

    metadatas = [
        {"category": "framework", "language": "python"},
        {"category": "library", "language": "python"},
        {"category": "server", "language": "python"},
    ]

    await rag.add_documents(documents, metadatas)

    # 검색
    results = await rag.retrieve("Python 프레임워크", top_k=3)
    for doc in results:
        logger.info(f"Score: {doc.score:.3f}")
        logger.info(f"Content: {doc.content}")
        logger.info(f"Metadata: {doc.metadata}")


async def example_rag_context_formatting():
    """RAGContext 포맷팅 예제"""
    logger.info("\n=== RAGContext 포맷팅 예제 ===")

    from .rag_interface import RAGContext, RAGDocument

    # RAGContext 생성
    documents = [
        RAGDocument(
            content="Open-LLM-VTuber는 오픈소스 프로젝트입니다.",
            score=0.85,
            metadata={"source": "README.md"},
        ),
        RAGDocument(
            content="FastAPI와 WebSocket을 사용합니다.",
            score=0.72,
            metadata={"source": "docs.md"},
        ),
    ]

    rag_context = RAGContext(
        documents=documents, query="프로젝트에 대해 알려줘", metadata={}
    )

    # 포맷된 문자열 출력
    formatted = rag_context.to_formatted_string(max_docs=2)
    logger.info("Formatted context:")
    logger.info(formatted)


async def example_incremental_addition():
    """점진적 문서 추가 예제"""
    logger.info("\n=== 점진적 문서 추가 예제 ===")

    rag = NaiveRAG(device="cpu")

    # 첫 번째 배치
    batch1 = ["문서 1: Python은 프로그래밍 언어입니다.", "문서 2: JavaScript는 웹 언어입니다."]
    await rag.add_documents(batch1)
    logger.info(f"After batch 1: {rag.get_index_size()} documents")

    # 두 번째 배치
    batch2 = ["문서 3: Rust는 시스템 프로그래밍 언어입니다.", "문서 4: Go는 구글이 만든 언어입니다."]
    await rag.add_documents(batch2)
    logger.info(f"After batch 2: {rag.get_index_size()} documents")

    # 검색
    results = await rag.retrieve("프로그래밍 언어", top_k=4)
    logger.info(f"Found {len(results)} results")


async def example_clear_index():
    """인덱스 초기화 예제"""
    logger.info("\n=== 인덱스 초기화 예제 ===")

    rag = NaiveRAG(device="cpu")

    # 문서 추가
    await rag.add_documents(["문서 1", "문서 2", "문서 3"])
    logger.info(f"Before clear: {rag.get_index_size()} documents")

    # 인덱스 초기화
    await rag.clear_index()
    logger.info(f"After clear: {rag.get_index_size()} documents")


async def main():
    """모든 예제 실행"""
    try:
        await example_basic_usage()
        await example_with_metadata()
        await example_rag_context_formatting()
        await example_incremental_addition()
        await example_clear_index()

        logger.info("\n✅ All examples completed successfully!")

    except Exception as e:
        logger.error(f"Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())

