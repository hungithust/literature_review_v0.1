# Architecture Document
## AI SOTA Radar MVP

---

## 1. System Overview

```
┌─────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────┐
│  Streamlit   │───▶│   Searcher    │───▶│   Filter     │───▶│  Summarizer  │───▶│  Results  │
│   (app.py)   │    │   Agent       │    │   Agent      │    │   Agent      │    │  Cards    │
└─────────────┘    └──────┬───────┘    └──────────────┘    └──────────────┘    └──────────┘
                          │
                    ┌─────┴──────┐
                    │  Clients    │
                    ├────────────┤
                    │ Semantic    │
                    │ Scholar API │
                    ├────────────┤
                    │ arXiv API   │
                    └────────────┘
```

## 2. Module Descriptions

### 2.1 `app.py` — Streamlit UI
- **Input**: User's Research Profile (text)
- **Output**: Rendered paper cards with scores and summaries
- **Responsibility**: UI only — no business logic

### 2.2 `workflow.py` — Pipeline Orchestrator
- **Input**: Research Profile string
- **Output**: List of `FinalPaperCard` objects
- **Responsibility**: Orchestrate the full pipeline: search → filter → summarize
- **Features**: Logging, timing, error handling per step

### 2.3 `agents/searcher.py` — Query Generator & Paper Fetcher
- **Input**: Research Profile
- **Output**: List of `PaperMetadata` (20-30 deduplicated papers)
- **Responsibility**: 
  - Extract keywords from profile
  - Generate 2-3 search queries
  - Call search clients
  - Merge and deduplicate results

### 2.4 `agents/filter.py` — Relevance Scorer
- **Input**: Research Profile + List of `PaperMetadata`
- **Output**: List of `FilterResult` (scored papers)
- **Responsibility**:
  - Score each paper 0-100 using LLM (OpenAI)
  - Evaluate domain fit, method fit, application fit
  - Return structured JSON with score, confidence, reason
  - Select top 3-5 papers

### 2.5 `agents/summarizer.py` — Paper Summarizer
- **Input**: Top papers (with metadata)
- **Output**: List of `SummaryResult`
- **Responsibility**:
  - Summarize each paper as problem / method / key_result
  - No hallucination — only use information from abstract
  - Return structured JSON

### 2.6 `clients/semantic_scholar_client.py`
- **Input**: Search query string, limit, date filter
- **Output**: List of `PaperMetadata`
- **API**: Semantic Scholar Academic Graph API (free, no key required for basic)

### 2.7 `clients/arxiv_client.py`
- **Input**: Search query string, limit
- **Output**: List of `PaperMetadata` (same schema)
- **API**: arXiv API (free, XML response)

### 2.8 `schemas.py` — Data Models
- `PaperMetadata`: title, abstract, authors, year, url, source
- `FilterResult`: paper_id, relevance_score, confidence, reason
- `SummaryResult`: paper_id, problem, method, key_result
- `FinalPaperCard`: combines all above for UI display

### 2.9 `utils/`
- `logger.py`: Structured logging setup
- `helpers.py`: Text cleaning, deduplication
- `validators.py`: JSON parsing, schema validation

## 3. Data Flow

```
Research Profile (str)
    │
    ▼
Searcher Agent
    ├── generates 2-3 queries
    ├── calls Semantic Scholar client
    ├── (optional) calls arXiv client
    ├── merges & deduplicates
    └── returns List[PaperMetadata] (~20-30 papers)
    │
    ▼
Filter Agent
    ├── sends each paper + profile to OpenAI
    ├── receives relevance_score + reason
    ├── ranks by score
    └── returns Top 3-5 List[FilterResult]
    │
    ▼
Summarizer Agent
    ├── sends each top paper to OpenAI
    ├── receives problem / method / key_result
    └── returns List[SummaryResult]
    │
    ▼
Workflow combines → List[FinalPaperCard]
    │
    ▼
Streamlit renders cards
```

## 4. External Dependencies
| Dependency | Purpose | Version |
|---|---|---|
| streamlit | Web UI | latest |
| httpx | HTTP client (async-capable) | latest |
| pydantic | Data validation & schemas | v2 |
| openai | LLM for filter & summarizer | latest |
| xmltodict | Parse arXiv XML responses | latest |
