# User Stories
## AI SOTA Radar MVP

---

## Core Stories

### US-1: Input Research Profile
**As a** researcher,  
**I want to** describe my research interests in natural language,  
**So that** the system understands what papers are relevant to me.

**Acceptance Criteria:**
- Text area accepting 50-500 characters of research description
- Pre-built sample profiles available for quick testing
- Profile is passed to the search pipeline

---

### US-2: Search for Recent Papers
**As a** researcher,  
**I want** the system to automatically find recent papers matching my profile,  
**So that** I don't have to manually search multiple sources.

**Acceptance Criteria:**
- System generates 2-3 search queries from my profile
- Papers are fetched from Semantic Scholar (primary) and arXiv (fallback)
- Results are deduplicated and normalized
- Target: 20-30 candidate papers

---

### US-3: Filter by Relevance
**As a** researcher,  
**I want** papers scored by how relevant they are to my specific interests,  
**So that** I only see the most pertinent ones.

**Acceptance Criteria:**
- Each paper gets a relevance score (0-100)
- Score considers domain fit, method fit, application fit
- Top 3-5 papers are selected
- Each scored paper has a brief reason explaining the score

---

### US-4: Read Structured Summaries
**As a** researcher,  
**I want** each top paper summarized in a structured format,  
**So that** I can quickly decide if it's worth reading the full paper.

**Acceptance Criteria:**
- Summary has 3 fields: problem, method, key_result
- Each field is 1-2 sentences max
- No hallucinated metrics or results
- Summary is based only on the abstract

---

### US-5: View Results in Dashboard
**As a** researcher,  
**I want** to see results displayed as cards on a clean dashboard,  
**So that** I can scan papers quickly.

**Acceptance Criteria:**
- Each card shows: title, authors, year, relevance score, reason, summary, link
- Cards are ordered by relevance score (descending)
- Loading state shown during processing
- Error messages are clear and user-friendly

---

### US-6: Handle Errors Gracefully
**As a** user,  
**I want** the app to handle API failures gracefully,  
**So that** I don't see cryptic error messages or crashes.

**Acceptance Criteria:**
- API timeout shows friendly message
- Empty results show "no papers found" message
- LLM parse errors are caught and logged
- App never shows raw stack traces to user
