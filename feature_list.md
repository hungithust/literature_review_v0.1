# Feature List
## AI SOTA Radar MVP

---

## Must-Have (MVP)

| # | Feature | Module | Priority |
|---|---------|--------|----------|
| F1 | Text input for Research Profile | app.py | P0 |
| F2 | Pre-built sample profiles | app.py, sample_profiles.json | P0 |
| F3 | Search papers from Semantic Scholar | clients/semantic_scholar_client.py | P0 |
| F4 | Search papers from arXiv (fallback) | clients/arxiv_client.py | P0 |
| F5 | Generate search queries from profile | agents/searcher.py | P0 |
| F6 | Deduplicate papers | agents/searcher.py | P0 |
| F7 | Score relevance (0-100) with LLM | agents/filter.py | P0 |
| F8 | Select Top 3-5 papers | agents/filter.py | P0 |
| F9 | Structured summary (problem/method/key_result) | agents/summarizer.py | P0 |
| F10 | Paper result cards in UI | app.py | P0 |
| F11 | Loading/progress indicator | app.py | P0 |
| F12 | Error handling & friendly messages | all modules | P0 |
| F13 | Logging per pipeline step | workflow.py, utils/logger.py | P0 |

## Nice-to-Have (Post-MVP)

| # | Feature | Notes |
|---|---------|-------|
| N1 | Date range filter for papers | Filter by last 7/30/90 days |
| N2 | Export results as PDF/Markdown | Save results for later |
| N3 | Multiple source aggregation | Add PubMed, OpenAlex |
| N4 | Batch scoring optimization | Score multiple papers in one LLM call |
| N5 | Profile history (local) | Remember last used profiles |
| N6 | Dark/light theme toggle | UI polish |

## Out of Scope

| Feature | Reason |
|---------|--------|
| User auth/registration | Not needed for MVP demo |
| Database (Firestore/Postgres) | No persistence needed |
| Bookmarking/favorites | Post-MVP feature |
| Notifications/email | Post-MVP feature |
| Admin dashboard | Not needed |
| Multi-user support | Single-user demo |
| Payment/subscription | Not applicable |
| Full-text paper crawling | Complex, out of scope |
| CI/CD pipeline | Not needed for demo |
