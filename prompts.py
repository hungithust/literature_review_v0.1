"""
Prompt templates for LLM-powered agents.

All prompts are centralized here for easy review and tuning.
"""

# --- Searcher Agent: Query Generation ---
QUERY_GENERATION_PROMPT = """You are a research paper search query generator.

Given a researcher's profile description, generate {num_queries} focused search queries
that would find the most relevant recent papers for this researcher.

Rules:
- Each query should be 3-7 words
- Focus on specific technical terms, not broad concepts
- Cover different aspects of the profile
- Do NOT generate overly broad queries like "machine learning" or "deep learning"
- Do NOT add year numbers to queries
- Queries should work well with academic search APIs

Research Profile:
{profile}

Return ONLY a JSON array of query strings. Example:
["query one", "query two", "query three"]
"""

# --- Filter Agent: Relevance Scoring ---
FILTER_SCORING_PROMPT = """You are a research paper relevance evaluator.

Given a researcher's profile and a paper's metadata, score how relevant this paper is
to the researcher's specific interests.

Scoring criteria (0-100):
- Domain fit (0-40): Is the paper in the same research domain?
- Method fit (0-30): Does it use methods the researcher works with?
- Application fit (0-30): Is the application area relevant?

Rules:
- A popular paper in a DIFFERENT domain should score LOW (< 30)
- A paper with a vague abstract should NOT automatically get a high score
- Do NOT score based on buzzwords alone
- Be specific in your reason

Research Profile:
{profile}

Paper Title: {title}
Paper Abstract: {abstract}

Return ONLY valid JSON in this exact format:
{{"relevance_score": <0-100>, "confidence": <0-100>, "reason": "<brief explanation>"}}
"""

# --- Filter Agent: Batch Scoring ---
FILTER_BATCH_SCORING_PROMPT = """You are a research paper relevance evaluator.

Given a researcher's profile and a list of papers, score how relevant each paper is.

Scoring criteria (0-100):
- Domain fit (0-40): Is the paper in the same research domain?
- Method fit (0-30): Does it use methods the researcher works with?
- Application fit (0-30): Is the application area relevant?

Rules:
- A popular paper in a DIFFERENT domain should score LOW (< 30)
- A paper with a vague abstract should NOT automatically get a high score
- Do NOT score based on buzzwords alone
- Be specific in your reason

Research Profile:
{profile}

Papers:
{papers_text}

Return ONLY a valid JSON array. Each element must have this exact format:
{{"paper_id": "<id>", "relevance_score": <0-100>, "confidence": <0-100>, "reason": "<brief explanation>"}}
"""

# --- Summarizer Agent: Paper Summary ---
SUMMARIZER_PROMPT = """You are a research paper summarizer for busy researchers.

Summarize the following paper based ONLY on the information provided (title + abstract).
Be concise and accurate. Do NOT hallucinate metrics, numbers, or results not mentioned.

Rules:
- Each field should be 1-2 sentences maximum
- If the abstract doesn't mention specific results, say "Results not specified in abstract"
- Use simple, clear language
- Focus on what makes this paper interesting or novel

Paper Title: {title}
Paper Abstract: {abstract}

Return ONLY valid JSON in this exact format:
{{"problem": "<what problem does the paper address>", "method": "<what method/approach is proposed>", "key_result": "<what is the key finding or result>"}}
"""
