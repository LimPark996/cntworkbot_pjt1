# 🏗️ 건설법령 AI 챗봇 — RAG 기반 법률 QA 시스템

> **건설/안전 법령 9종을 학습한 AI 챗봇**  
> PDF 원문 → 법률 구조 인식 청킹 → 하이브리드 검색(FAISS + BM25 + Cross-encoder Reranking) → 질의 유형별 맞춤 답변 생성

<br>

## 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **목적** | 건설/안전 법령에 대한 정확한 답변을 제공하는 RAG 기반 AI 챗봇 |
| **팀 구성** | 5명 (팀장 겸 강사 1명 + 팀원 4명) |
| **도메인** | 건축법, 건설산업기본법, 산업안전보건 등 9종 법령 |
| **핵심 기술** | Hybrid Search (FAISS + BM25), RRF, Cross-encoder Reranking, GPT-4o |
| **특징** | 질의 유형 7종 자동 분류 → 유형별 맞춤 프롬프트로 답변 생성 |
| **부가 성과** | 비전공자 대상 4일간 RAG 실습 강의 진행 및 팀 발표 완수 |

<br>

## 시스템 아키텍처

```
┌─────────────────── Data Pipeline ───────────────────┐
│                                                      │
│  📄 PDF 법령 9종                                     │
│      ↓                                               │
│  [S1] PDF Processor ─→ 페이지별 텍스트 추출           │
│      ↓                                               │
│  [S2] Document Merger ─→ 통합 문서 구조 생성          │
│      ↓                                               │
│  [S3] Legal Chunking ─→ 조(條)/항(項) 단위 청킹      │
│      │  └─ 800 tokens, 200 overlap                   │
│      ↓                                               │
│  [S4] Embedding Manager                              │
│      ├─ OpenAI text-embedding-3-large (3072-dim)     │
│      ├─ MD5 기반 캐시로 중복 API 호출 방지             │
│      └─→ FAISS IndexFlatL2 구축                      │
│                                                      │
└──────────────────────────────────────────────────────┘

┌─────────────────── Search Pipeline ─────────────────┐
│                                                      │
│  사용자 질의                                          │
│      ↓                                               │
│  [S6.1] Query Classifier (GPT-4o-mini)               │
│      │  └─ 7종 질의 유형 자동 분류                     │
│      ↓                                               │
│  [S5] Hybrid Search Engine                           │
│      ├─ Vector Search (FAISS) ─┐                     │
│      ├─ Keyword Search (BM25) ─┤                     │
│      │                         ↓                     │
│      ├─ Reciprocal Rank Fusion (k=60)                │
│      └─ Cross-encoder Reranking                      │
│         └─ BAAI/bge-reranker-base                    │
│      ↓                                               │
│  [S6.2] Answer Generator (GPT-4o)                    │
│      ├─ 유형별 맞춤 시스템 프롬프트                     │
│      ├─ Grounding 원칙: 문서 내 근거만 인용             │
│      └─ 환각 방지: 근거 없으면 "찾을 수 없습니다" 명시   │
│      ↓                                               │
│  Streamlit Chat UI                                   │
│      └─ 답변 + 출처 + 문서 생성/다운로드               │
│                                                      │
└──────────────────────────────────────────────────────┘
```

<br>

## 기술 스택

| 레이어 | 기술 | 선택 이유 |
|--------|------|-----------|
| PDF 파싱 | pdfplumber | 표/레이아웃 보존, 한글 지원 우수 |
| 토큰 계산 | tiktoken | GPT 모델과 동일한 토크나이저로 정확한 청크 사이즈 보장 |
| 임베딩 | OpenAI text-embedding-3-large | 3072차원, 법률 도메인 의미 포착 최적 |
| 벡터 검색 | FAISS IndexFlatL2 | 정확한 최근접 이웃 검색 (근사 아닌 정확 검색) |
| 키워드 검색 | BM25 (rank-bm25) | "제36조" 등 정확한 법조문 번호 매칭에 필수 |
| 리랭킹 | BAAI/bge-reranker-base | 경량 Cross-encoder, Query-Document 쌍 직접 비교 |
| LLM | GPT-4o / GPT-4o-mini | 답변 생성 / 질의 분류 |
| 웹 UI | Streamlit | 빠른 프로토타이핑, 채팅 인터페이스 기본 제공 |

<br>

## 왜 하이브리드 검색인가?

| 검색 방식 | 강점 | 약점 |
|-----------|------|------|
| **Vector Search** | 의미적 유사도 포착 ("안전 조치" ↔ "보호 대책") | 정확한 법조문 번호 매칭 약함 |
| **BM25** | 키워드 정확 매칭 ("제36조", "건폐율") | 동의어/유사 표현 매칭 불가 |
| **Hybrid + RRF** | 두 방식의 강점 결합, 순위 정규화 | — |
| **+ Reranking** | Cross-encoder로 최종 관련성 정밀 판별 | — |

법률 도메인은 **정확한 조문 번호**와 **의미적 맥락** 모두 중요하기 때문에, 단일 검색 방식으로는 부족합니다.

<br>

## 질의 유형 분류 (7종)

| 유형 | 예시 | 검색 | 답변 형식 |
|------|------|------|-----------|
| 일상 대화 | "안녕하세요" | X | 자연스러운 인사 |
| 법조문 조회 | "제36조가 뭐야?" | O | 조문 원문 + 해설 |
| 일반 정보 검색 | "비계 안전 기준?" | O | 근거 기반 설명 |
| 상황별 컨설팅 | "3m 비계 설치 적법한가?" | O | 적법/부적법 판단 + 근거 |
| 절차 안내 | "용도변경 절차?" | O | 단계별 안내 |
| 문서 생성 | "안전 체크리스트 만들어줘" | O | 법적필수 + 실무권장 구분 |
| 비교 분석 | "건축법과 건설산업기본법 차이?" | O | 항목별 대조표 |

<br>

## 프로젝트 구조

```
├── src/
│   ├── s1_PDFProcessor.py          # PDF → 페이지별 텍스트 JSON
│   ├── s2_DocumentMerger.py         # 다중 문서 통합
│   ├── s3_LegalChunkingStrategy.py  # 조/항 단위 법률 청킹
│   ├── s4_EmbeddingManager.py       # 임베딩 + FAISS 인덱스
│   ├── s5_LegalSearchEngine.py      # 하이브리드 검색 엔진
│   ├── s61_QueryClassifier.py       # 질의 유형 분류기
│   ├── s62_GPTLegalSearchSystem.py  # 유형별 답변 생성기
│   ├── TestQAApp.py                 # Streamlit 웹 UI
│   └── TestCompletedFlow.py         # 통합 테스트
│
├── notebooks/                       # 비전공자 실습 교안 (4일 과정)
│   ├── s1_PDFProcessor.ipynb        # Day 1: PDF 파싱 기초
│   ├── s2_DocumentMerger.ipynb      # Day 1: 데이터 통합
│   ├── s3_LegalChunkingStrategy.ipynb # Day 2: 청킹 전략
│   ├── s4_EmbeddingManager.ipynb    # Day 2: 임베딩과 벡터DB
│   └── s5_LegalSearchEngine.ipynb   # Day 3: 검색 엔진 구축
│
├── config/
│   └── document_types.json          # 문서 유형 매핑
│
├── data/
│   ├── raw/                         # PDF 원본 (9종)
│   ├── processed/                   # 추출된 텍스트 JSON
│   ├── chunks/                      # 청킹 결과
│   └── vector_store/                # FAISS 인덱스 + 메타데이터
│
└── requirements.txt
```

<br>

## 실행 방법

### 1. 환경 설정

```bash
pip install -r requirements.txt
```

### 2. API 키 설정

```bash
# .env 파일 생성
echo "OPENAI_API_KEY='your-api-key'" > .env
```

### 3. 데이터 파이프라인 실행 (최초 1회)

```bash
# PDF 추출 → 통합 → 청킹 → 임베딩 → 인덱스 구축
python src/s1_PDFProcessor.py
python src/s2_DocumentMerger.py
python src/s3_LegalChunkingStrategy.py
python src/s4_EmbeddingManager.py
```

### 4. 챗봇 실행

```bash
streamlit run src/TestQAApp.py
```

<br>

## 비전공자 교육 과정 (4일)

이 프로젝트의 각 파이프라인 단계를 **비전공자도 따라할 수 있는 실습 교안**으로 제작하여, 팀원 3명을 대상으로 4일간 강의를 진행했습니다.

| Day | 주제 | 학습 목표 | 실습 (ToDo) |
|-----|------|-----------|-------------|
| 1 | PDF 파서 + 문서 통합 | 함수, 클래스, 파일 I/O, 데이터 구조 | PDF→JSON 변환 + 다중 문서 병합 |
| 2 | 법률 청킹 + 임베딩 | 정규식, 토큰, API 활용, 캐싱 | 조/항 분할 + OpenAI 임베딩 + FAISS |
| 3 | 검색 엔진 + 질의 분류/답변 | 정보 검색 이론, 프롬프트 설계 | 하이브리드 검색 + GPT 답변 생성 |
| 4 | Streamlit 챗봇 + 보강 | 웹 앱 개발, 통합 실습 | 웹 UI 구축 + 어려운 부분 복습 |

각 노트북은 **이론 설명 → 함수 단위 실습(ToDo) → 클래스 통합 → 실행 및 검증** 순서로 구성되어 있습니다.

<br>

## 환각 방지 전략

법률 도메인에서 **잘못된 정보 생성(환각)은 치명적**이기 때문에, 다음 전략을 적용했습니다:

1. **Grounding 원칙** — 검색된 문서에 있는 내용만 답변
2. **근거 없으면 명시** — "제공된 문서에서 찾을 수 없습니다"
3. **추측 금지** — "일반적으로", "보통" 등 모호한 표현 사용 금지
4. **출처 표시** — 답변마다 참조한 법령명, 조항 표기
5. **유형별 프롬프트** — 질의 유형에 따라 다른 시스템 프롬프트로 정밀도 향상

<br>

## 향후 개선 방향

- [ ] Agent 패턴 적용 (Tool-use 기반 법령 검색/문서 생성 자동화)
- [ ] 평가 파이프라인 구축 (Retrieval Accuracy, Answer Relevance 정량 측정)
- [ ] Docker 컨테이너화
- [ ] 대화 이력 기반 멀티턴 QA 지원
