# Product Requirements Document (PRD)
## AI SOTA Radar — Personalized Daily Research Paper Tracker

---

## 1. Pain Point

Researchers and AI practitioners spend **hours daily** scanning arXiv, Semantic Scholar, and Twitter for relevant new papers. Most papers are irrelevant to their specific research focus. There is no simple tool that:
- Understands a researcher's specific interests (beyond broad keywords)
- Automatically filters papers by true relevance (not just keyword match)
- Provides concise, structured summaries to decide whether to read further

## 2. User Persona

**Primary User: AI/ML Researcher or Practitioner**
- PhD students, postdocs, research engineers
- Actively working on a specific research area (e.g., LLMs, protein prediction, GNNs)
- Reads 5-20 paper abstracts daily
- Wants to reduce scanning time from 60 minutes to 10 minutes
- Comfortable with English academic content
- Not necessarily technical enough to build their own pipeline

## 3. MVP Goal

Build a **working demo** that:
1. Accepts a Research Profile (text description of research interests)
2. Searches for recent papers from Semantic Scholar (with arXiv as fallback)
3. Scores each paper's relevance to the profile (0-100)
4. Selects Top 3-5 most relevant papers
5. Generates structured summaries (problem / method / key_result)
6. Displays results in a clean Streamlit dashboard

## 4. Success Criteria
- Pipeline runs end-to-end without crashes
- Results are relevant (not random/keyword-only matches)
- Summaries are accurate (no hallucinated metrics)
- Demo takes < 60 seconds to produce results
- Non-technical user can operate the UI

## 5. Out of Scope (MVP)
- User authentication / registration
- Database storage (Firestore, Postgres, etc.)
- Bookmarking / history
- Notifications
- Multi-user system
- Admin dashboard
- Payment integration
- CI/CD production deployment
- Full-text paper crawling
