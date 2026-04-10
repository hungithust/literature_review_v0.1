# Test Scenarios
## AI SOTA Radar MVP

---

## TC-1: Happy Path — NLP Profile
**Input**: "Deep Learning for NLP, LLMs, retrieval-augmented generation, instruction tuning"  
**Expected**:
- Searcher generates 2-3 relevant queries
- 20-30 papers fetched
- Top 3-5 papers are about LLMs/NLP (not random CV or bio papers)
- Summaries are structured and accurate
- UI displays all cards correctly

---

## TC-2: Niche Profile — Protein Prediction
**Input**: "AI for protein function prediction, biological sequences, representation learning"  
**Expected**:
- Papers are from computational biology / bioinformatics
- Filter correctly identifies papers about protein/bio, not generic ML
- Summaries don't hallucinate biological metrics

---

## TC-3: Empty Results
**Input**: "xyzzy quantum underwater basket weaving neural networks for invisible cats"  
**Expected**:
- Semantic Scholar returns 0 or very few results
- arXiv fallback is attempted
- UI shows friendly "No papers found" message
- No crash or stack trace

---

## TC-4: API Timeout / Failure
**Scenario**: Simulate API being down or timing out  
**Expected**:
- Client catches timeout exception
- Error is logged with clear message
- UI shows user-friendly error (not raw exception)
- App remains usable (can retry)

---

## TC-5: Paper with Missing Abstract
**Scenario**: Some papers returned have null/empty abstracts  
**Expected**:
- Papers without abstracts are either skipped or marked
- Filter handles missing abstract gracefully (lower score or skip)
- Summarizer does not hallucinate content for missing abstracts
- No JSON parse errors

---

## TC-6: Broad Profile
**Input**: "Machine learning"  
**Expected**:
- Searcher doesn't generate overly broad queries
- Results are not random/noisy
- Filter still produces reasonable ranking
- System completes within reasonable time (<90 seconds)

---

## TC-7: LLM Output Malformed
**Scenario**: LLM returns invalid JSON or unexpected format  
**Expected**:
- JSON parser catches the error
- Fallback/default values are used or paper is skipped
- Error is logged
- Pipeline continues processing remaining papers

---

## TC-8: Duplicate Papers Across Sources
**Scenario**: Same paper appears in both Semantic Scholar and arXiv results  
**Expected**:
- Deduplication removes the duplicate
- Only one copy appears in final results
- Metadata from the better source is preferred

---

## TC-9: Multiple Consecutive Runs
**Scenario**: User runs pipeline 3 times with same profile  
**Expected**:
- Results are consistent (similar papers, similar scores)
- No memory leaks or state pollution
- Each run completes successfully

---

## TC-10: Special Characters in Profile
**Input**: "GNN & graph neural networks for drug discovery (2024-2025)"  
**Expected**:
- Special characters don't break query generation
- API calls handle encoded characters properly
- Results are relevant to GNN/drug discovery
