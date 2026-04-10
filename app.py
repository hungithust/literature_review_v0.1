"""
AI SOTA Radar — Streamlit Dashboard.

Main entry point for the web application.
Provides a clean UI for inputting research profiles
and viewing paper recommendations.
"""

import json
import sys
import os
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import run_pipeline
from schemas import FinalPaperCard


# --- Page Configuration ---
st.set_page_config(
    page_title="AI SOTA Radar",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
    /* Global styles */
    .main > div { padding-top: 1rem; }

    /* Header */
    .app-header {
        text-align: center;
        padding: 1.5rem 0;
        margin-bottom: 1rem;
    }
    .app-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem;
        font-weight: 800;
        margin-bottom: 0.3rem;
    }
    .app-header p {
        color: #6b7280;
        font-size: 1.1rem;
    }

    /* Paper card */
    .paper-card {
        background: linear-gradient(135deg, #f8f9ff 0%, #f0f4ff 100%);
        border: 1px solid #e0e7ff;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .paper-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }

    .paper-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.4rem;
        line-height: 1.4;
    }
    .paper-title a {
        color: #4f46e5;
        text-decoration: none;
    }
    .paper-title a:hover {
        text-decoration: underline;
    }

    .paper-meta {
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 0.8rem;
    }

    .score-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.9rem;
        margin-right: 0.5rem;
    }
    .score-high { background: #dcfce7; color: #166534; }
    .score-medium { background: #fef3c7; color: #92400e; }
    .score-low { background: #fee2e2; color: #991b1b; }

    .reason-text {
        color: #4b5563;
        font-size: 0.9rem;
        font-style: italic;
        margin: 0.5rem 0;
        padding-left: 0.8rem;
        border-left: 3px solid #818cf8;
    }

    .summary-section {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 0.8rem;
    }
    .summary-label {
        font-weight: 600;
        color: #4f46e5;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .summary-text {
        color: #374151;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
    }

    /* Stats bar */
    .stats-bar {
        display: flex;
        gap: 1.5rem;
        padding: 1rem;
        background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%);
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .stat-item { text-align: center; flex: 1; }
    .stat-number { font-size: 1.5rem; font-weight: 800; color: #4f46e5; }
    .stat-label { font-size: 0.8rem; color: #6b7280; }
</style>
""", unsafe_allow_html=True)


def main():
    """Main application entry point."""

    # --- Header ---
    st.markdown("""
    <div class="app-header">
        <h1>🔬 AI SOTA Radar</h1>
        <p>Personalized Research Paper Tracker — Find the most relevant papers for your research</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        st.header("📋 Research Profile")
        st.caption("Describe your research interests to find relevant papers.")

        # Load sample profiles
        sample_profiles = _load_sample_profiles()
        profile_names = ["✍️ Custom"] + [p["name"] for p in sample_profiles]

        selected_profile = st.selectbox(
            "Choose a profile or write your own:",
            profile_names,
            index=0,
        )

        if selected_profile == "✍️ Custom":
            profile_text = st.text_area(
                "Describe your research interests:",
                placeholder="e.g., Deep learning for NLP, large language models, retrieval-augmented generation, instruction tuning",
                height=120,
            )
        else:
            # Find selected sample profile
            profile_data = next(
                (p for p in sample_profiles if p["name"] == selected_profile),
                None,
            )
            profile_text = profile_data["description"] if profile_data else ""
            st.text_area(
                "Profile description:",
                value=profile_text,
                height=120,
                disabled=True,
            )

        st.divider()

        # Settings
        st.header("⚙️ Settings")
        top_k = st.slider("Number of top papers", min_value=3, max_value=10, value=5)

        st.divider()

        run_button = st.button(
            "🚀 Find Papers",
            type="primary",
            use_container_width=True,
            disabled=not profile_text,
        )

    # --- Main Content ---
    if run_button and profile_text:
        _run_and_display(profile_text, top_k)
    elif "results" in st.session_state and st.session_state.results:
        _display_results(st.session_state.results)
    else:
        _display_welcome()


def _run_and_display(profile: str, top_k: int):
    """Run the pipeline and display results."""
    progress_bar = st.progress(0, text="Starting pipeline...")
    status_text = st.empty()

    def progress_callback(message: str, step: int, total: int):
        progress_bar.progress(step / total, text=message)
        status_text.info(message)

    with st.spinner("Running AI SOTA Radar pipeline..."):
        try:
            # Temporarily override top_k in config
            import config
            original_top_k = config.FILTER_TOP_K
            config.FILTER_TOP_K = top_k

            results = run_pipeline(profile, progress_callback=progress_callback)

            config.FILTER_TOP_K = original_top_k

        except Exception as err:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Pipeline failed: {str(err)}")
            st.info("Please check your OpenAI API key and internet connection, then try again.")
            return

    progress_bar.empty()
    status_text.empty()

    if not results:
        st.warning("🔍 No relevant papers found for this profile. Try adjusting your research description.")
        return

    # Save to session state
    st.session_state.results = results
    st.session_state.profile = profile

    _display_results(results)


def _display_results(results: list[FinalPaperCard]):
    """Display paper results as cards."""

    # Stats bar
    avg_score = sum(r.relevance_score for r in results) / len(results) if results else 0
    sources = set(r.source for r in results)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📄 Papers Found", len(results))
    with col2:
        st.metric("📊 Avg. Relevance", f"{avg_score:.0f}/100")
    with col3:
        st.metric("🔗 Sources", ", ".join(s.replace("_", " ").title() for s in sources))

    st.divider()

    # Paper cards
    for i, card in enumerate(results):
        _render_paper_card(card, rank=i + 1)


def _render_paper_card(card: FinalPaperCard, rank: int):
    """Render a single paper card."""

    # Score badge color
    if card.relevance_score >= 70:
        score_class = "score-high"
    elif card.relevance_score >= 40:
        score_class = "score-medium"
    else:
        score_class = "score-low"

    # Authors display
    authors_display = ", ".join(card.authors[:3])
    if len(card.authors) > 3:
        authors_display += f" +{len(card.authors) - 3} more"

    # Title with link
    title_html = f'<a href="{card.url}" target="_blank">{card.title}</a>' if card.url else card.title

    st.markdown(f"""
    <div class="paper-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div style="flex: 1;">
                <div class="paper-title">#{rank} {title_html}</div>
                <div class="paper-meta">
                    👤 {authors_display} &nbsp;|&nbsp; 📅 {card.year or 'N/A'} &nbsp;|&nbsp;
                    📦 {card.source.replace('_', ' ').title()}
                </div>
            </div>
            <div>
                <span class="score-badge {score_class}">{card.relevance_score}/100</span>
            </div>
        </div>

        <div class="reason-text">{card.relevance_reason}</div>

        <div class="summary-section">
            <div><span class="summary-label">🎯 Problem: </span><span class="summary-text">{card.problem}</span></div>
            <div><span class="summary-label">🔧 Method: </span><span class="summary-text">{card.method}</span></div>
            <div><span class="summary-label">📈 Key Result: </span><span class="summary-text">{card.key_result}</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _display_welcome():
    """Display welcome message when no results are loaded."""
    st.markdown("""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h2 style="color: #4f46e5;">Welcome to AI SOTA Radar</h2>
        <p style="color: #6b7280; font-size: 1.1rem; max-width: 600px; margin: 0 auto;">
            Describe your research interests in the sidebar, then click
            <strong>🚀 Find Papers</strong> to discover the most relevant
            recent papers personalized for you.
        </p>
        <div style="margin-top: 2rem; display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap;">
            <div style="background: #f0f4ff; padding: 1.5rem; border-radius: 12px; width: 200px;">
                <div style="font-size: 2rem;">🔍</div>
                <div style="font-weight: 600; color: #1e293b;">Smart Search</div>
                <div style="color: #6b7280; font-size: 0.85rem;">AI-generated queries from your profile</div>
            </div>
            <div style="background: #f0fdf4; padding: 1.5rem; border-radius: 12px; width: 200px;">
                <div style="font-size: 2rem;">🎯</div>
                <div style="font-weight: 600; color: #1e293b;">Relevance Filter</div>
                <div style="color: #6b7280; font-size: 0.85rem;">LLM-powered scoring for each paper</div>
            </div>
            <div style="background: #fef3c7; padding: 1.5rem; border-radius: 12px; width: 200px;">
                <div style="font-size: 2rem;">📝</div>
                <div style="font-weight: 600; color: #1e293b;">Smart Summary</div>
                <div style="color: #6b7280; font-size: 0.85rem;">Structured problem/method/result</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def _load_sample_profiles() -> list[dict]:
    """Load sample profiles from JSON file."""
    try:
        profiles_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "sample_profiles.json",
        )
        with open(profiles_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as err:
        st.sidebar.warning(f"Could not load sample profiles: {err}")
        return []


if __name__ == "__main__":
    main()
