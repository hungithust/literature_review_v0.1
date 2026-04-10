# Demo Cases
## AI SOTA Radar

---

## Demo Case 1: NLP Researcher

**Profile**: "Deep Learning for NLP, large language models, retrieval-augmented generation, instruction tuning, prompt engineering"

**Expected Behavior**:
- System generates queries like "retrieval augmented generation", "instruction tuning LLM", "prompt engineering methods"
- Top papers should be about RAG, instruction tuning, or LLM methods
- Scores should clearly differentiate NLP papers from unrelated ones
- Summaries should accurately describe the NLP techniques

**How to demo**: Select "NLP & Large Language Models" from the sidebar dropdown.

---

## Demo Case 2: Computational Biology

**Profile**: "AI for protein function prediction, biological sequence modeling, protein representation learning, structure prediction"

**Expected Behavior**:
- Papers focus on protein/bioML, not generic deep learning
- Filter correctly assigns lower scores to papers that only tangentially mention proteins
- Summaries reference biological concepts accurately (no hallucinated metrics)

**How to demo**: Select "AI for Protein Science" from the sidebar dropdown.

---

## Demo Case 3: Custom Niche Topic

**Profile**: "Diffusion models for medical image synthesis and augmentation in radiology, focusing on chest X-ray generation"

**Expected Behavior**:
- System finds papers at the intersection of diffusion models + medical imaging
- Papers about generic diffusion models (e.g., for natural images) score lower
- Papers about chest X-ray or medical radiology score highest
- Demonstrates that custom profiles work beyond pre-built options

**How to demo**: Select "✍️ Custom" and paste the profile above.
