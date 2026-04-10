# Backlog
## AI SOTA Radar MVP

---

## Task 1: Planning Documents
| File | Status | DoD |
|------|--------|-----|
| PRD.md | ✅ Done | Pain point, persona, MVP goal, out-of-scope defined |
| user_stories.md | ✅ Done | 6 user stories with acceptance criteria |
| architecture.md | ✅ Done | Module descriptions, data flow, dependencies |
| feature_list.md | ✅ Done | Must-have / nice-to-have / out-of-scope categorized |
| test_scenarios.md | ✅ Done | 10 test scenarios including error cases |
| backlog.md | ✅ Done | This file |

## Task 2: Project Skeleton
| Item | Status | DoD |
|------|--------|-----|
| Directory structure | ⬜ | All folders and __init__.py created |
| schemas.py | ⬜ | PaperMetadata, FilterResult, SummaryResult, FinalPaperCard |
| config.py | ⬜ | API keys, limits, feature flags |
| prompts.py | ⬜ | Prompt templates for filter and summarizer |
| requirements.txt | ⬜ | All dependencies listed |

## Task 3: Search Clients
| Item | Status | DoD |
|------|--------|-----|
| semantic_scholar_client.py | ⬜ | Query → List[PaperMetadata], handles timeout/empty |
| arxiv_client.py | ⬜ | Query → List[PaperMetadata], same schema as SS |

## Task 4: Searcher Agent
| Item | Status | DoD |
|------|--------|-----|
| agents/searcher.py | ⬜ | Profile → 2-3 queries → fetch → dedup → 20-30 papers |

## Task 5: Filter Agent
| Item | Status | DoD |
|------|--------|-----|
| agents/filter.py | ⬜ | Score 0-100, JSON output, selects top 3-5 |

## Task 6: Summarizer Agent
| Item | Status | DoD |
|------|--------|-----|
| agents/summarizer.py | ⬜ | problem/method/key_result JSON, no hallucination |

## Task 7: Workflow
| Item | Status | DoD |
|------|--------|-----|
| workflow.py | ⬜ | run_pipeline() → full results, logging, error handling |

## Task 8: Streamlit UI
| Item | Status | DoD |
|------|--------|-----|
| app.py | ⬜ | Profile input, run button, result cards, loading, errors |

## Task 9: Test Data
| Item | Status | DoD |
|------|--------|-----|
| sample_profiles.json | ⬜ | 5 profiles (NLP, multimodal, protein, time-series, GNN) |
| tests/ | ⬜ | Basic unit tests for searcher, filter, summarizer |

## Task 10: Polish
| Item | Status | DoD |
|------|--------|-----|
| README.md | ⬜ | Setup instructions, usage, demo screenshots |
| demo_cases.md | ⬜ | 2-3 stable demo cases |
| UI polish | ⬜ | Clean layout, no bugs |
