# Storybook Mode Architecture

## 📖 개요

이 문서는 Open-LLM-VTuber의 Storybook Mode가 어떻게 동화책 캐릭터의 세계관을 주입하고, 모든 질문을 동화책 관점으로 해석하여 답변하는지 설명합니다.

## 🎯 핵심 원리

### 세계관 주입 방식: **프롬프트 + RAG 컨텍스트 조합**

단순히 프롬프트만으로 주입되는 것이 **아니라**, 두 가지가 함께 작동합니다:

#### 1️⃣ 정적 프롬프트 (행동 지침)
`storybook_constraint_prompt.txt`는 **"어떻게 답변할지"**에 대한 지침만 제공:
- "동화책 세계관으로 해석하라"
- "가치관을 적용하라"
- "창의적으로 연결하라"
- "절대 캐릭터를 깨지 마라"

#### 2️⃣ 동적 RAG 컨텍스트 (실제 세계관 내용)
매 질문마다 RAG가 **실제 동화책 내용**을 검색하여 제공:
- 캐릭터 정보
- 장소 설명
- 사건 내용
- 가치관과 교훈

## 🔄 전체 동작 흐름

### 예시: "스마트폰이 뭐야?" 질문

```
┌─────────────────────────────────────────────────────────┐
│ 사용자: "스마트폰이 뭐야?"                                │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 1. RAG 검색 (single_conversation.py)                    │
│    - Query: "스마트폰이 뭐야?"                            │
│    - 임베딩 생성 및 유사도 검색                           │
│    - 동화책에서 관련 내용 찾음:                           │
│      * "Great Oak Tree can speak wisdom"                │
│      * "magical Stream Stone glows with blue light"     │
│      * "trees can whisper secrets"                      │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 2. 프롬프트 구성 (basic_memory_agent.py)                │
│                                                          │
│ [시스템 프롬프트] - 서버 시작 시 구성                     │
│   ├─ 캐릭터 페르소나 (persona_prompt)                    │
│   │   "You are Finn, a curious fox..."                 │
│   └─ 세계관 제약 (storybook_constraint_prompt)          │
│       "Interpret everything through your story's lens..." │
│                                                          │
│ [유저 메시지] - 매 질문마다 동적 구성                     │
│   === Your Story World Knowledge ===                    │
│   [Story Knowledge 1 (relevance: 0.45)]                 │
│   The Great Oak Tree can speak wisdom to all...         │
│                                                          │
│   [Story Knowledge 2 (relevance: 0.38)]                 │
│   The Stream Stone is a magical crystal...              │
│                                                          │
│   Using your story's values, interpret: "스마트폰이 뭐야?" │
│   ===                                                    │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 3. LLM 추론                                              │
│    - RAG 컨텍스트에서 "wisdom", "speak", "magical" 발견  │
│    - 프롬프트 지침에 따라 해석:                           │
│      "smart phone" → "wise tree you can carry"          │
│    - 동화책 톤으로 답변 생성                              │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│ 4. 최종 답변                                             │
│    "A phone that's smart? How curious! In the           │
│    Whispering Woods, we have the Great Oak Tree who     │
│    can speak wisdom to all who listen. Perhaps your     │
│    'smart phone' is like a wise tree you can carry      │
│    with you? That sounds like powerful magic!"          │
└─────────────────────────────────────────────────────────┘
```

## 📂 코드 엔트리 포인트

### 1. 서버 시작 시: 동화책 로딩

**파일**: `src/dreamtale/service_context.py`

```python
async def init_rag(self, rag_config: RAGConfig) -> None:
    """RAG 엔진 초기화 및 동화책 자동 로딩"""
    
    # RAG 엔진 초기화
    self.rag_engine = RAGFactory.get_rag_engine(
        rag_config.rag_type,
        **getattr(rag_config, rag_config.rag_type).model_dump(),
    )
    
    # 동화책 자동 로딩
    if rag_config.auto_load_storybook:
        await self._load_storybook_documents(rag_config)
```

**호출 경로**:
```
run_server.py
  └─> ServiceContext.load_from_config()
      └─> ServiceContext.init_rag()
          └─> ServiceContext._load_storybook_documents()
              └─> document_loader.load_storybook_documents()
```

**동작**:
1. `storybooks/{conf_uid}/` 디렉토리에서 모든 `.txt`, `.md` 파일 로드
2. 각 파일을 청크로 분할 (기본: 300 단어, 50 단어 오버랩)
3. 임베딩 생성 및 RAG 인덱스에 추가

### 2. 서버 시작 시: 시스템 프롬프트 구성

**파일**: `src/dreamtale/service_context.py`

```python
async def construct_system_prompt(self, persona_prompt: str) -> str:
    """시스템 프롬프트 구성"""
    
    # 1. 기본 페르소나 프롬프트
    system_prompt = persona_prompt
    
    # 2. 도구 프롬프트 추가 (live2d_expression 등)
    for prompt_name, prompt_file in self.system_config.tool_prompts.items():
        prompt_content = prompt_loader.load_util(prompt_file)
        system_prompt += prompt_content
    
    # 3. 동화책 제약 프롬프트 추가
    if self.character_config.storybook_title:
        storybook_constraint = prompt_loader.load_util(
            "storybook_constraint_prompt"
        )
        system_prompt += storybook_constraint
    
    return system_prompt
```

**호출 경로**:
```
ServiceContext.init_agent()
  └─> ServiceContext.construct_system_prompt()
      └─> prompt_loader.load_util("storybook_constraint_prompt")
```

### 3. 매 질문마다: RAG 검색

**파일**: `src/dreamtale/conversations/single_conversation.py`

```python
async def process_single_conversation(...):
    """단일 대화 처리"""
    
    # 사용자 입력 처리
    input_text = await process_user_input(user_input, asr_engine, websocket_send)
    
    # RAG 검색 수행
    rag_context = None
    if context.rag_engine and context.character_config.rag_config.enabled:
        # 관련 문서 검색
        documents = await context.rag_engine.retrieve(
            query=input_text,
            top_k=top_k,
            min_score=min_score,
        )
        
        if documents:
            # RAG 컨텍스트 생성
            rag_context = RAGContext(
                documents=documents,
                query=input_text,
                metadata={"retrieval_time": "now"}
            )
    
    # BatchInput에 RAG 컨텍스트 추가
    batch_input = create_batch_input(...)
    if rag_context:
        batch_input.rag_context = rag_context
    
    # Agent에게 전달
    agent_output_stream = context.agent_engine.chat(batch_input)
```

**호출 경로**:
```
WebSocket 메시지 수신
  └─> handle_conversation_trigger()
      └─> process_single_conversation()
          └─> context.rag_engine.retrieve()
              └─> NaiveRAG.retrieve()
```

### 4. 매 질문마다: RAG 컨텍스트 포맷팅

**파일**: `src/dreamtale/agent/agents/basic_memory_agent.py`

```python
def _format_rag_context(self, rag_context) -> str:
    """RAG 컨텍스트를 프롬프트용으로 포맷"""
    
    # 동화책 모드 확인
    is_storybook = any(
        doc.metadata and "storybook" in doc.metadata.get("source", "").lower()
        for doc in rag_context.documents
    )
    
    if is_storybook:
        # 동화책 전용 포맷
        formatted_parts = [
            "=== Your Story World Knowledge ===",
            "The following information from your story world helps you...",
            "",
        ]
        
        for i, doc in enumerate(rag_context.documents, 1):
            formatted_parts.append(f"[Story Knowledge {i}]")
            formatted_parts.append(doc.content)
            formatted_parts.append("")
        
        formatted_parts.append(
            "Using your story's values, interpret and answer naturally..."
        )
        
    return "\n".join(formatted_parts)

def _to_messages(self, input_data: BatchInput) -> List[Dict[str, Any]]:
    """LLM API 호출용 메시지 구성"""
    
    messages = self._memory.copy()
    text_prompt = self._to_text_prompt(input_data)
    
    # RAG 컨텍스트 추가
    if input_data.rag_context and input_data.rag_context.documents:
        rag_formatted = self._format_rag_context(input_data.rag_context)
        if rag_formatted:
            # RAG 컨텍스트를 유저 프롬프트 앞에 추가
            text_prompt = f"{rag_formatted}\n\n{text_prompt}"
    
    messages.append({"role": "user", "content": text_prompt})
    return messages
```

**호출 경로**:
```
process_single_conversation()
  └─> agent_engine.chat(batch_input)
      └─> BasicMemoryAgent.chat()
          └─> BasicMemoryAgent._to_messages()
              └─> BasicMemoryAgent._format_rag_context()
```

## 🏗️ 시스템 아키텍처

### 전체 구성 요소

```
┌─────────────────────────────────────────────────────────────┐
│                    서버 시작 시 (1회)                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 동화책 로딩 (service_context.py)                         │
│     storybooks/{conf_uid}/*.txt → RAG 인덱스                │
│                                                              │
│  2. 시스템 프롬프트 구성 (service_context.py)                │
│     persona_prompt                                           │
│     + tool_prompts                                           │
│     + storybook_constraint_prompt                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                  매 질문마다 (반복)                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  3. RAG 검색 (single_conversation.py)                        │
│     사용자 질문 → 임베딩 → 유사도 검색 → 관련 문서 추출      │
│                                                              │
│  4. 프롬프트 구성 (basic_memory_agent.py)                    │
│     [시스템] 페르소나 + 제약                                  │
│     [유저] RAG 컨텍스트 + 질문                               │
│                                                              │
│  5. LLM 추론                                                 │
│     동화책 지식 기반 해석 → 창의적 답변 생성                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 데이터 흐름

```
[설정 파일]
conf.yaml
  ├─ persona_prompt: "You are Finn, a curious fox..."
  ├─ storybook_title: "The Little Fox's Adventure"
  └─ rag_config:
      ├─ enabled: true
      ├─ auto_load_storybook: true
      └─ storybook_directory: "storybooks"

[동화책 파일]
storybooks/example_story_001/
  ├─ story.txt        → 45 chunks
  ├─ characters.txt   → 12 chunks
  └─ world.txt        → 18 chunks
                        ↓
                  [RAG 인덱스]
                  75 document chunks
                  with embeddings
                        ↓
[사용자 질문] "스마트폰이 뭐야?"
                        ↓
                  [RAG 검색]
                  Query embedding
                  Cosine similarity
                        ↓
                  [검색 결과]
                  Top 3 chunks:
                  1. Great Oak Tree (0.45)
                  2. Stream Stone (0.38)
                  3. Whisper secrets (0.32)
                        ↓
                  [프롬프트 구성]
                  System: persona + constraint
                  User: RAG context + question
                        ↓
                  [LLM 추론]
                        ↓
                  [답변 생성]
```

## 📝 주요 파일 및 역할

### 설정 파일

| 파일 | 역할 | 내용 |
|------|------|------|
| `config_templates/conf.default.yaml` | 기본 설정 템플릿 | 기본 persona_prompt, RAG 설정 예시 |
| `characters/{character}.yaml` | 캐릭터별 설정 | 구체적인 persona_prompt, rag_config |
| `conf.yaml` | 실제 사용 설정 | 사용자가 선택한 설정 |

### 프롬프트 파일

| 파일 | 역할 | 언제 로드 |
|------|------|----------|
| `prompts/utils/storybook_constraint_prompt.txt` | 세계관 해석 지침 | 서버 시작 시 (storybook_title 있으면) |
| `prompts/utils/live2d_expression_prompt.txt` | 표정 제어 지침 | 서버 시작 시 (항상) |

### 동화책 파일

| 위치 | 역할 | 형식 |
|------|------|------|
| `storybooks/{conf_uid}/*.txt` | 동화책 내용 | 텍스트 파일 |
| `storybooks/{conf_uid}/*.md` | 동화책 내용 | 마크다운 파일 |

### 소스 코드

| 파일 | 주요 함수/클래스 | 역할 |
|------|-----------------|------|
| `src/dreamtale/service_context.py` | `init_rag()`, `_load_storybook_documents()`, `construct_system_prompt()` | RAG 초기화, 동화책 로딩, 프롬프트 구성 |
| `src/dreamtale/conversations/single_conversation.py` | `process_single_conversation()` | RAG 검색 및 대화 처리 |
| `src/dreamtale/agent/agents/basic_memory_agent.py` | `_format_rag_context()`, `_to_messages()` | RAG 컨텍스트 포맷팅 |
| `src/dreamtale/rag/document_loader.py` | `load_storybook_documents()`, `chunk_text()` | 동화책 파일 로딩 및 청킹 |
| `src/dreamtale/rag/naive_rag.py` | `NaiveRAG.retrieve()` | 벡터 검색 및 문서 추출 |

## 🔍 상세 예시

### 예시 1: 기술 관련 질문

**질문**: "컴퓨터가 뭐야?"

**RAG 검색 결과**:
```
[Document 1 - score: 0.42]
The Stream Stone is a magical crystal that can control
the flow of water throughout the forest.

[Document 2 - score: 0.35]
The Great Oak Tree has wisdom and can solve problems
for all the forest animals.

[Document 3 - score: 0.31]
Finn and his friends worked together to solve the
puzzle of the tangled vines.
```

**LLM에게 전달되는 프롬프트**:
```
[SYSTEM]
You are Finn, a curious fox from the Whispering Woods...
Interpret everything through your story's lens...

[USER]
=== Your Story World Knowledge ===
[Story Knowledge 1]
The Stream Stone is a magical crystal that can control
the flow of water throughout the forest.

[Story Knowledge 2]
The Great Oak Tree has wisdom and can solve problems...

Using your story's values, interpret: "컴퓨터가 뭐야?"
===
```

**예상 답변**:
> "컴퓨터? 그건 문제를 풀 수 있는 마법 같은 거야? 우리 숲에는 위대한 참나무가 있어서 모든 동물들의 문제를 풀어줘. 그리고 스트림 스톤은 마법의 수정인데, 숲 전체의 물 흐름을 조절할 수 있어! 네 '컴퓨터'도 그런 마법 같은 돌인가봐? 많은 일들을 할 수 있는?"

### 예시 2: 추상적 개념 질문

**질문**: "우정이 뭐라고 생각해?"

**RAG 검색 결과**:
```
[Document 1 - score: 0.68]
Finn, Bella, Oliver, and Daisy worked together to save
the Singing Stream. Each friend used their unique gifts.

[Document 2 - score: 0.65]
Through this adventure, they learned the importance of
patience, teamwork, and friendship.

[Document 3 - score: 0.58]
When friends work together and use their unique gifts,
they can overcome any challenge.
```

**예상 답변**:
> "우정은 정말 특별한 거야! 우리가 노래하는 시냇물을 구할 때, 나 혼자서는 할 수 없었어. 벨라는 땅을 파는 걸 도와주고, 올리버는 높은 곳의 덩굴을 풀어주고, 데이지는 힘으로 덩굴을 당겨줬어. 각자의 특별한 재능을 함께 사용했을 때, 우리는 어떤 어려움도 이겨낼 수 있었어! 우정은 서로를 돕고, 함께 있을 때 더 강해지는 거야!"

## 🎯 핵심 포인트

### 1. 이중 주입 시스템

- **정적 프롬프트**: "어떻게 생각할 것인가" (서버 시작 시 1회)
- **동적 RAG**: "무엇을 알고 있는가" (매 질문마다)

### 2. 창의적 해석

- 모든 질문을 **거부하지 않고** 동화책 세계관으로 해석
- 동화책의 유사 개념을 찾아 연결
- 캐릭터의 경험과 가치관을 적용

### 3. 컨텍스트 기반 답변

- RAG가 제공하는 실제 동화책 내용을 기반으로 답변
- 추측이나 일반 지식이 아닌 **스토리 내 사실**에 근거

### 4. 몰입 유지

- 절대 "모른다"고 하지 않음
- 절대 캐릭터를 깨지 않음
- 자연스럽고 교육적인 답변 제공

## 🚀 확장 가능성

### 현재 구현

- ✅ 텍스트 기반 동화책 로딩
- ✅ 의미 기반 검색 (semantic search)
- ✅ 동적 컨텍스트 주입
- ✅ 창의적 해석 지침

### 향후 개선 방향

- 🔮 메타데이터 기반 필터링 (캐릭터별, 장소별, 시간대별)
- 🔮 대화 히스토리 기반 컨텍스트 우선순위 조정
- 🔮 멀티모달 RAG (이미지, 오디오 포함)
- 🔮 동적 동화책 업데이트 (실시간 내용 추가)
- 🔮 캐릭터 간 지식 공유 (같은 동화책의 다른 캐릭터)

## 📚 참고 문서

- [STORYBOOK_MODE.md](STORYBOOK_MODE.md) - 사용자 가이드
- [RAG_IMPLEMENTATION.md](RAG_IMPLEMENTATION.md) - RAG 기술 상세
- [RAG_QUICKSTART.md](RAG_QUICKSTART.md) - RAG 빠른 시작
- [storybooks/README.md](storybooks/README.md) - 동화책 파일 구성

---

**작성일**: 2025-11-28  
**버전**: v1.0.0  
**작성자**: AI Coding Assistant

