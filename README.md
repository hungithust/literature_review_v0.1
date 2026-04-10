# AI SOTA Radar 🔬

**Personalized Daily Research Paper Tracker**

AI SOTA Radar helps researchers discover the most relevant recent papers by understanding their research interests and using AI to filter and summarize results.

## Features

- 🔍 **Smart Search**: AI generates targeted search queries from your research profile
- 🎯 **Relevance Filtering**: LLM-powered scoring (0-100) evaluates domain, method, and application fit
- 📝 **Structured Summaries**: Each paper is summarized as problem / method / key result
- 📊 **Clean Dashboard**: Streamlit-based UI with paper cards, scores, and explanations

## Quick Start

### 1. Prerequisites

- Python 3.11+
- OpenAI API key

### 2. Install Dependencies

```bash
cd ai-sota-radar
pip install -r requirements.txt
```

### 3. Set API Key

```bash
# Windows PowerShell
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac
export OPENAI_API_KEY="your-api-key-here"
```

### 4. Run the App

```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`.

## Usage

1. **Select or write a Research Profile** in the sidebar
2. Click **🚀 Find Papers**
3. Wait for the pipeline to complete (~30-60 seconds)
4. Browse paper cards sorted by relevance

## Sample Profiles

The app comes with 5 pre-built profiles:

| Profile | Focus Area |
|---------|------------|
| NLP & LLMs | Deep learning for NLP, retrieval-augmented generation, instruction tuning |
| Multimodal Learning | Vision-language models, cross-modal alignment |
| AI for Protein Science | Protein prediction, biological sequences |
| Time-Series Forecasting | Temporal transformers, foundation models |
| Graph Neural Networks | GNN for scientific/biomedical applications |

## Architecture

```
app.py (Streamlit UI)
  └─▶ workflow.py (Pipeline Orchestrator)
        ├─▶ agents/searcher.py (Query Generation + Paper Fetch)
        │     ├─▶ clients/semantic_scholar_client.py
        │     └─▶ clients/arxiv_client.py
        ├─▶ agents/filter.py (Relevance Scoring via OpenAI)
        └─▶ agents/summarizer.py (Paper Summarization via OpenAI)
```

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `OPENAI_API_KEY` | (required) | OpenAI API key |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model to use |
| `ENABLE_ARXIV_FALLBACK` | `true` | Use arXiv when Semantic Scholar returns few results |
| `ENABLE_ARXIV_ALWAYS` | `false` | Always include arXiv results |
| `LOG_LEVEL` | `INFO` | Logging level |

## Running Tests

```bash
python tests/test_searcher.py
python tests/test_filter.py
python tests/test_summarizer.py
```

## Tech Stack

- **Python 3.11** — Core language
- **Streamlit** — Web UI framework
- **OpenAI (gpt-4o-mini)** — LLM for filtering & summarization
- **Semantic Scholar API** — Primary paper source
- **arXiv API** — Fallback paper source
- **Pydantic v2** — Data validation
- **httpx** — HTTP client
