# 🏗️ 건설법령 AI 챗봇

건설사 실무진을 위한 법령 검색 및 문서 생성 RAG 챗봇입니다.

---

## ✨ 주요 기능

| 기능 | 설명 |
|------|------|
| 🔍 **하이브리드 검색** | FAISS 벡터 + BM25 키워드 + Reranker |
| 🤖 **GPT 질문 분류** | 7가지 유형 자동 분류 (법조문 조회, 컨설팅, 문서 생성 등) |
| 📝 **문서 생성** | 체크리스트, 점검표 자동 생성 + PDF 다운로드 |
| 📚 **출처 표시** | 법령명, 조항, 페이지 번호 명시 |

---

## 📚 사용 데이터 (data/raw)

| 파일명 | 내용 |
|--------|------|
| (AURI)해석례로 읽는 건축법.pdf | 건축법 질의응답 사례집 |
| (국가법령정보센터)건축법.pdf | 건축법 전문 |
| 건설공사발주자의 산업안전보건업무 가이드북.pdf | 발주자 안전관리 가이드 |
| 건설산업기본법(법률)(제20357호).pdf | 건설산업기본법 |
| 건축법 시행규칙(국토교통부령)(제01531호).pdf | 건축법 시행규칙 |
| 건축법 시행령(대통령령)(제35811호).pdf | 건축법 시행령 |
| 건축법(법률)(제21065호).pdf | 건축법 본법 |
| 국토의 계획 및 이용에 관한 법률 시행령.pdf | 국토계획법 시행령 |
| 산업안전보건기준에 관한 규칙.pdf | 산업안전보건 규칙 |

---

## 🚀 빠른 시작

### 1. 환경 설정

```bash
# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일 생성:
```
OPENAI_API_KEY=your_api_key_here
```

### 3. 데이터 파이프라인 실행

```bash
# 1단계: PDF 파싱
python src/s1_PDFProcessor.py

# 2단계: 문서 통합
python src/s2_DocumentMerger.py

# 3단계: 청킹
python src/s3_LegalChunkingStrategy.py

# 4단계: 임베딩 + FAISS 인덱스 생성
python src/s4_EmbeddingManager.py

# (선택) 전체 파이프라인 한 번에 실행
python src/TestCompletedFlow.py
```

### 4. 챗봇 실행

```bash
streamlit run src/TestQAApp.py
```

---

## 📁 프로젝트 구조

```
project/
├── src/
│   ├── TestQAApp.py                # Streamlit 메인 앱 ⭐
│   ├── TestCompletedFlow.py        # 전체 파이프라인 테스트
│   ├── s1_PDFProcessor.py          # PDF 텍스트 추출
│   ├── s2_DocumentMerger.py        # 문서 통합
│   ├── s3_LegalChunkingStrategy.py # 법령 특화 청킹
│   ├── s4_EmbeddingManager.py      # 임베딩 + FAISS
│   ├── s5_LegalSearchEngine.py     # 하이브리드 검색
│   ├── s61_QueryClassifier.py      # GPT 질문 분류
│   └── s62_GPTLegalSearchSystem.py # QA 시스템
├── data/
│   ├── raw/                        # 원본 PDF (9개)
│   ├── processed/                  # 파싱된 JSON
│   ├── chunks/                     # 청킹된 JSON
│   ├── vector_store/               # FAISS 인덱스
│   └── cache/                      # 임베딩 캐시
├── .env                            # API 키
└── requirements.txt
```

---

## 🔧 RAG 파이프라인

```
[1. PDF 파싱] ─────────────────────────────────────────────────────
    │  pdfplumber로 텍스트 추출
    │  → data/processed/*_processed.json
    ▼
[2. 문서 통합] ────────────────────────────────────────────────────
    │  9개 문서를 하나의 JSON으로 병합
    │  → data/processed/construction_law_unified.json
    ▼
[3. 청킹] ─────────────────────────────────────────────────────────
    │  법령 구조 인식 (제N조, ①②③, 가.나.다.)
    │  토큰 기반 분할 (800토큰, 200 오버랩)
    │  → data/chunks/construction_law_chunks.json
    ▼
[4. 임베딩 + FAISS] ───────────────────────────────────────────────
    │  OpenAI text-embedding-3-large (3072차원)
    │  → data/vector_store/faiss_index.bin
    │  → data/vector_store/metadata.json
    ▼
[5. 하이브리드 검색] ──────────────────────────────────────────────
    │  FAISS 벡터 검색
    │  BM25 키워드 검색 (선택)
    │  Cross-encoder Reranker (bge-reranker-base)
    ▼
[6. GPT 답변 생성] ────────────────────────────────────────────────
    │  질문 유형 분류 → 유형별 프롬프트
    │  JSON 구조화 답변 → 자연어 변환
    ▼
[Streamlit UI] ────────────────────────────────────────────────────
    실시간 진행 상황 표시 + 문서 편집기 + PDF 다운로드
```

---

## 🎯 질문 유형 (7가지)

| 유형 | 설명 | 예시 |
|------|------|------|
| 🔴 법조문_조회 | 특정 조항 내용 요청 | "제36조 내용 알려줘" |
| 🟢 일반_정보_검색 | 법적 기준/규정 질문 | "비계 안전 기준은?" |
| 🔵 상황별_컨설팅 | 현장 상황 법적 판단 | "3m 비계 설치해도 되나요?" |
| 🟡 절차_안내 | 행정 절차 단계별 안내 | "용도변경 절차 알려줘" |
| 🟠 문서_생성 | 체크리스트/양식 생성 | "비계 점검표 만들어줘" |
| 🟣 비교_분석 | 법령/개념 비교 | "건축법과 건설산업기본법 차이" |
| ⚪ 일상_대화 | 인사/잡담 | "안녕하세요" |

---

## 🛠️ 기술 스택

### requirements.txt

```txt
# PDF 처리
pdfplumber>=0.10.0

# 텍스트 처리 및 토큰화
tiktoken>=0.5.0

# OpenAI API
openai>=1.0.0

# 벡터 검색
faiss-cpu>=1.7.4
numpy>=1.24.0

# 키워드 검색
rank-bm25>=0.2.2

# Reranker 처리
sentence-transformers>=2.2.0

# 환경변수
python-dotenv>=1.0.0

# 웹 UI
streamlit>=1.28.0

# PDF 생성
reportlab>=4.0.0
```

### 핵심 기술

| 구분 | 기술 |
|------|------|
| LLM | GPT-4o-mini (분류/답변) |
| 임베딩 | text-embedding-3-large (3072D) |
| 벡터 DB | FAISS (IndexFlatL2) |
| 키워드 검색 | BM25 (rank-bm25) |
| Reranker | bge-reranker-base |
| PDF 파싱 | pdfplumber |
| 웹 UI | Streamlit |
| PDF 생성 | ReportLab |

---

## 💡 사용 예시

### 기본 질문
```
Q: 건폐율 계산 방법 알려줘
Q: 비계 설치 안전 기준은?
Q: 건축허가 신청 절차
```

### 문서 생성
```
Q: 비계 점검 체크리스트 만들어줘
Q: 굴착작업 안전점검표 작성해줘
→ 편집기에서 수정 후 TXT/PDF 다운로드
```

### 상황별 컨설팅
```
Q: 우리 현장에서 3m 높이 비계 설치하는데 문제없나요?
Q: 안전관리자 1명으로 충분한가요? 현장 인원 50명입니다
```

---

## ⚠️ Hallucination 방지

시스템 프롬프트에 Grounding 규칙 적용:

```
🚨 핵심 원칙
1. 제공된 [관련 법령 정보]에 있는 내용만 답변
2. 문서에 없으면 "제공된 문서에서 해당 내용을 찾을 수 없습니다" 답변
3. 추측하거나 일반 지식으로 보충 금지
4. 부분적으로만 답변 가능하면 나머지는 "확인 불가" 표시
```

---

## 📝 면책 조항

- 본 챗봇은 법률 자문을 대체하지 않습니다
- 중요한 결정은 반드시 전문가 검토를 받으세요
- 최신 법령 개정 사항은 [국가법령정보센터](https://www.law.go.kr)에서 확인하세요

---

## 👥 개발 정보

- **교육 과정**: 삼성물산 AI Academy 전문코스
- **프로젝트 기간**: 2025.11.24 ~ 11.27
- **강사**: 박유미