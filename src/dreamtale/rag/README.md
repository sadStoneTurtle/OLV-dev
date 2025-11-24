# RAG (Retrieval-Augmented Generation) Module

이 모듈은 Open-LLM-VTuber에 RAG 기능을 제공합니다.

## 📋 개요

RAG는 외부 지식 베이스에서 관련 정보를 검색하여 LLM의 응답을 향상시키는 기술입니다. 이 구현은 다음을 제공합니다:

- **유연한 인터페이스**: 다양한 RAG 백엔드 지원 (SimpleRAG, ChromaDB, FAISS 등)
- **비동기 처리**: 모든 작업이 async/await로 구현됨
- **자동 통합**: 대화 파이프라인에 자동으로 통합됨

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
uv add sentence-transformers
```

### 2. 설정 파일 수정 (`conf.yaml`)

```yaml
character_config:
  # ... 기존 설정 ...
  
  rag_config:
    enabled: true  # RAG 활성화
    rag_type: "simple"  # RAG 엔진 타입
    include_in_prompt: true  # 프롬프트에 컨텍스트 포함
    max_context_docs: 3  # 최대 문서 수
    
    simple:
      model_name: "sentence-transformers/all-MiniLM-L6-v2"
      device: "cpu"  # 또는 "cuda", "mps"
      top_k: 3  # 검색할 문서 수
      min_score: 0.3  # 최소 유사도 점수
```

### 3. 문서 추가

```python
from src.dreamtale.rag import SimpleRAG

# RAG 엔진 초기화
rag_engine = SimpleRAG(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    device="cpu"
)

# 문서 추가
documents = [
    "Open-LLM-VTuber는 오픈소스 VTuber 프로젝트입니다.",
    "FastAPI를 사용하여 WebSocket 서버를 구현합니다.",
    "Live2D 모델을 지원하며 실시간 표정 변화가 가능합니다.",
]

await rag_engine.add_documents(documents)

# 검색
results = await rag_engine.retrieve("VTuber 프로젝트에 대해 알려줘", top_k=2)
for doc in results:
    print(f"Score: {doc.score:.3f}, Content: {doc.content}")
```

## 📁 모듈 구조

```
rag/
├── __init__.py              # 모듈 초기화
├── rag_interface.py         # RAG 인터페이스 정의
├── rag_factory.py           # RAG 엔진 팩토리
├── simple_rag.py            # SimpleRAG 구현 (in-memory)
└── README.md                # 이 문서
```

## 🔧 구현된 RAG 엔진

### SimpleRAG

**특징:**
- In-memory 벡터 저장소
- sentence-transformers 사용
- 코사인 유사도 기반 검색
- 소규모~중규모 데이터셋에 적합

**장점:**
- 설정이 간단함
- 외부 의존성 최소화
- 빠른 프로토타이핑

**단점:**
- 메모리에만 저장 (재시작 시 데이터 손실)
- 대규모 데이터셋에는 부적합

### 향후 지원 예정

- **ChromaDB**: 영구 저장소, 메타데이터 필터링
- **FAISS**: 대규모 벡터 검색 최적화
- **Weaviate**: 클라우드 네이티브 벡터 DB

## 🔌 통합 방식

RAG는 다음 지점에서 통합됩니다:

1. **`BatchInput`** (`agent/input_types.py`)
   - `rag_context` 필드 추가
   - RAG 검색 결과 저장

2. **`ServiceContext`** (`service_context.py`)
   - `rag_engine` 인스턴스 관리
   - `init_rag()` 메서드로 초기화

3. **`single_conversation.py`**
   - Agent 호출 전 RAG 검색 수행
   - 검색 결과를 `BatchInput`에 추가

4. **`basic_memory_agent.py`**
   - `_to_messages()`에서 RAG 컨텍스트를 프롬프트에 추가
   - LLM에게 전달

## 📊 데이터 흐름

```
사용자 입력
    ↓
single_conversation.py
    ├─ RAG 검색 수행
    ├─ RAGContext 생성
    └─ BatchInput에 추가
    ↓
basic_memory_agent.py
    ├─ RAG 컨텍스트를 프롬프트에 포함
    └─ LLM 호출
    ↓
응답 생성
```

## 🎯 사용 예제

### 예제 1: 프로젝트 문서 RAG

```python
# 프로젝트 README 파일을 RAG에 추가
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()
    
# 문단별로 분할
paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]

await rag_engine.add_documents(
    documents=paragraphs,
    metadatas=[{"source": "README.md", "index": i} for i in range(len(paragraphs))]
)
```

### 예제 2: FAQ 시스템

```python
faqs = [
    "Q: 설치 방법은? A: uv sync 명령어를 실행하세요.",
    "Q: 지원하는 TTS는? A: Azure TTS, Edge TTS, MeloTTS 등을 지원합니다.",
    "Q: Live2D 모델 추가 방법은? A: live2d-models 폴더에 모델을 추가하세요.",
]

await rag_engine.add_documents(faqs)
```

### 예제 3: 대화 히스토리 검색

```python
# 과거 대화 내용을 RAG에 추가하여 장기 기억 구현
from src.dreamtale.chat_history_manager import get_history

messages = get_history(conf_uid="default", history_uid="some_history")
conversation_texts = [
    f"{msg['role']}: {msg['content']}" 
    for msg in messages
]

await rag_engine.add_documents(conversation_texts)
```

## ⚙️ 고급 설정

### 커스텀 임베딩 모델

```yaml
rag_config:
  simple:
    model_name: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    # 다국어 지원이 더 좋은 모델
```

### GPU 사용

```yaml
rag_config:
  simple:
    device: "cuda"  # NVIDIA GPU
    # 또는
    device: "mps"   # Apple Silicon
```

### 검색 파라미터 조정

```yaml
rag_config:
  simple:
    top_k: 5  # 더 많은 문서 검색
    min_score: 0.5  # 더 높은 유사도 요구
```

## 🐛 트러블슈팅

### 문제: "sentence_transformers를 찾을 수 없습니다"

**해결:**
```bash
uv add sentence-transformers
```

### 문제: GPU 메모리 부족

**해결:**
```yaml
rag_config:
  simple:
    device: "cpu"  # CPU로 변경
```

### 문제: 검색 결과가 없음

**해결:**
1. `min_score`를 낮춰보세요 (예: 0.1)
2. 문서가 제대로 추가되었는지 확인:
   ```python
   print(f"Index size: {rag_engine.get_index_size()}")
   ```

## 📝 라이선스

이 모듈은 Open-LLM-VTuber 프로젝트의 일부이며 동일한 라이선스를 따릅니다.

