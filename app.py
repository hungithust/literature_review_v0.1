"""
AI SOTA Radar — Streamlit Dashboard.

Main entry point for the web application.
Provides a clean UI for inputting research profiles
and viewing paper recommendations.
Includes Firebase Authentication (Email/Password + Google).
"""

import json
import sys
import os
import streamlit as st

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from workflow import run_pipeline
from schemas import FinalPaperCard
from config import FIREBASE_API_KEY, GOOGLE_CLIENT_ID


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
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Inter', sans-serif; }

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

    /* Auth page styles */
    .auth-container {
        max-width: 440px;
        margin: 0 auto;
        padding: 2.5rem;
        background: linear-gradient(145deg, #ffffff 0%, #f8f9ff 100%);
        border-radius: 24px;
        border: 1px solid #e0e7ff;
        box-shadow: 0 20px 60px rgba(102, 126, 234, 0.08),
                    0 4px 16px rgba(0, 0, 0, 0.04);
    }
    .auth-title {
        text-align: center;
        font-size: 1.6rem;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 0.3rem;
    }
    .auth-subtitle {
        text-align: center;
        color: #6b7280;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }

    .auth-divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
        color: #9ca3af;
        font-size: 0.85rem;
    }
    .auth-divider::before,
    .auth-divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid #e5e7eb;
    }
    .auth-divider::before { margin-right: 1rem; }
    .auth-divider::after { margin-left: 1rem; }

    /* Google button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        width: 100%;
        padding: 0.75rem 1.5rem;
        background: white;
        border: 1.5px solid #dadce0;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #3c4043;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
    }
    .google-btn:hover {
        background: #f8f9fa;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-color: #c0c0c0;
    }
    .google-btn img {
        width: 20px;
        height: 20px;
    }

    /* User bar */
    .user-bar {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.8rem 1rem;
        background: linear-gradient(135deg, #ede9fe 0%, #e0e7ff 100%);
        border-radius: 12px;
        margin-bottom: 1rem;
    }
    .user-avatar {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: 700;
        font-size: 1rem;
    }
    .user-email {
        color: #4338ca;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .user-label {
        color: #6b7280;
        font-size: 0.75rem;
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

    /* Streamlit overrides for auth forms */
    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 1.5px solid #e0e7ff !important;
        padding: 0.6rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }

    /* Success animation */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .auth-success {
        animation: fadeInUp 0.5s ease-out;
        text-align: center;
        padding: 2rem;
    }
    .auth-success .check-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Auth helpers
# ──────────────────────────────────────────────

def _init_session_state():
    """Initialize auth-related session state."""
    defaults = {
        "authenticated": False,
        "user_email": None,
        "user_id": None,
        "auth_token": None,
        "refresh_token": None,
        "display_name": None,
        "photo_url": None,
        "results": None,
        "profile": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _set_user_session(user_data: dict):
    """Store user info in Streamlit session."""
    st.session_state.authenticated = True
    st.session_state.user_email = user_data.get("email", "")
    st.session_state.user_id = user_data.get("user_id", "")
    st.session_state.auth_token = user_data.get("token", "")
    st.session_state.refresh_token = user_data.get("refresh_token", "")
    st.session_state.display_name = user_data.get("display_name", "")
    st.session_state.photo_url = user_data.get("photo_url", "")


def _clear_user_session():
    """Clear user session on logout."""
    st.session_state.authenticated = False
    st.session_state.user_email = None
    st.session_state.user_id = None
    st.session_state.auth_token = None
    st.session_state.refresh_token = None
    st.session_state.display_name = None
    st.session_state.photo_url = None
    st.session_state.results = None
    st.session_state.profile = None


def _parse_firebase_error(err: Exception) -> str:
    """Extract human-readable error from Firebase exceptions."""
    error_str = str(err)
    error_map = {
        "EMAIL_EXISTS": "Email này đã được đăng ký. Vui lòng đăng nhập.",
        "EMAIL_NOT_FOUND": "Email không tồn tại. Vui lòng đăng ký tài khoản mới.",
        "INVALID_PASSWORD": "Mật khẩu không đúng. Vui lòng thử lại.",
        "INVALID_EMAIL": "Email không hợp lệ.",
        "WEAK_PASSWORD": "Mật khẩu phải có ít nhất 6 ký tự.",
        "USER_DISABLED": "Tài khoản đã bị vô hiệu hóa.",
        "TOO_MANY_ATTEMPTS_TRY_LATER": "Quá nhiều lần thử. Vui lòng thử lại sau.",
        "INVALID_LOGIN_CREDENTIALS": "Email hoặc mật khẩu không đúng.",
    }
    for key, message in error_map.items():
        if key in error_str:
            return message
    return f"Lỗi xác thực: {error_str}"


# ──────────────────────────────────────────────
#  Auth UI
# ──────────────────────────────────────────────

def _render_auth_page():
    """Render the login/signup page."""

    # Header
    st.markdown("""
    <div class="app-header">
        <h1>🔬 AI SOTA Radar</h1>
        <p>Personalized Research Paper Tracker</p>
    </div>
    """, unsafe_allow_html=True)

    # Check if Firebase is configured
    if not FIREBASE_API_KEY:
        st.warning(
            "⚠️ Firebase chưa được cấu hình. Vui lòng thêm `FIREBASE_API_KEY` và các biến khác vào file `.env`.\n\n"
            "Đang chuyển sang chế độ **không cần đăng nhập** để demo..."
        )
        st.divider()
        if st.button("🚀 Tiếp tục không cần đăng nhập (Demo Mode)", type="primary", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.user_email = "demo@ai-sota-radar.local"
            st.session_state.display_name = "Demo User"
            st.rerun()
        return

    # Auth container
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)

        # Tab selection
        tab_login, tab_signup = st.tabs(["🔐 Đăng nhập", "📝 Đăng ký"])

        # ─── Login Tab ───
        with tab_login:
            st.markdown('<p class="auth-title">Chào mừng trở lại!</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-subtitle">Đăng nhập để truy cập AI SOTA Radar</p>', unsafe_allow_html=True)

            with st.form("login_form", clear_on_submit=False):
                login_email = st.text_input(
                    "📧 Email",
                    placeholder="you@example.com",
                    key="login_email_input",
                )
                login_password = st.text_input(
                    "🔑 Mật khẩu",
                    type="password",
                    placeholder="Nhập mật khẩu",
                    key="login_password_input",
                )
                login_submit = st.form_submit_button(
                    "🔐 Đăng nhập",
                    type="primary",
                    use_container_width=True,
                )

            if login_submit:
                if not login_email or not login_password:
                    st.error("Vui lòng nhập email và mật khẩu.")
                else:
                    _handle_email_login(login_email, login_password)

            # Divider
            st.markdown('<div class="auth-divider">hoặc</div>', unsafe_allow_html=True)

            # Google Sign-In button
            _render_google_signin_button()

        # ─── Signup Tab ───
        with tab_signup:
            st.markdown('<p class="auth-title">Tạo tài khoản mới</p>', unsafe_allow_html=True)
            st.markdown('<p class="auth-subtitle">Đăng ký để bắt đầu theo dõi nghiên cứu</p>', unsafe_allow_html=True)

            with st.form("signup_form", clear_on_submit=False):
                signup_email = st.text_input(
                    "📧 Email",
                    placeholder="you@example.com",
                    key="signup_email_input",
                )
                signup_password = st.text_input(
                    "🔑 Mật khẩu",
                    type="password",
                    placeholder="Ít nhất 6 ký tự",
                    key="signup_password_input",
                )
                signup_confirm = st.text_input(
                    "🔑 Xác nhận mật khẩu",
                    type="password",
                    placeholder="Nhập lại mật khẩu",
                    key="signup_confirm_input",
                )
                signup_submit = st.form_submit_button(
                    "📝 Đăng ký",
                    type="primary",
                    use_container_width=True,
                )

            if signup_submit:
                if not signup_email or not signup_password:
                    st.error("Vui lòng nhập đầy đủ thông tin.")
                elif signup_password != signup_confirm:
                    st.error("Mật khẩu xác nhận không khớp.")
                elif len(signup_password) < 6:
                    st.error("Mật khẩu phải có ít nhất 6 ký tự.")
                else:
                    _handle_email_signup(signup_email, signup_password)

            # Divider
            st.markdown('<div class="auth-divider">hoặc</div>', unsafe_allow_html=True)

            # Google Sign-In button
            _render_google_signin_button(key_suffix="signup")

        st.markdown('</div>', unsafe_allow_html=True)


def _handle_email_login(email: str, password: str):
    """Handle email/password login."""
    try:
        from auth.firebase_auth import sign_in_with_email
        with st.spinner("Đang đăng nhập..."):
            user_data = sign_in_with_email(email, password)
        _set_user_session(user_data)
        st.success("✅ Đăng nhập thành công!")
        st.rerun()
    except Exception as err:
        st.error(_parse_firebase_error(err))


def _handle_email_signup(email: str, password: str):
    """Handle email/password signup."""
    try:
        from auth.firebase_auth import sign_up_with_email
        with st.spinner("Đang tạo tài khoản..."):
            user_data = sign_up_with_email(email, password)
        _set_user_session(user_data)
        st.success("✅ Tạo tài khoản thành công! Đang chuyển hướng...")
        st.rerun()
    except Exception as err:
        st.error(_parse_firebase_error(err))


def _render_google_signin_button(key_suffix: str = "login"):
    """Render Google Sign-In using OAuth2 redirect flow with native Streamlit button."""
    if not GOOGLE_CLIENT_ID:
        st.info("💡 Để bật đăng nhập Google, hãy thêm `GOOGLE_CLIENT_ID` vào file `.env`")
        return

    # Check for Google token in query params (callback from OAuth)
    query_params = st.query_params
    google_token = query_params.get("google_token", None)

    if google_token:
        try:
            from auth.firebase_auth import sign_in_with_google_token
            with st.spinner("Đang đăng nhập với Google..."):
                user_data = sign_in_with_google_token(google_token)
            _set_user_session(user_data)
            st.query_params.clear()
            st.success("✅ Đăng nhập Google thành công!")
            st.rerun()
        except Exception as err:
            st.query_params.clear()
            st.error(f"Lỗi đăng nhập Google: {_parse_firebase_error(err)}")
        return

    # Build Google OAuth2 authorization URL
    import urllib.parse
    redirect_uri = "http://localhost:8501"
    oauth_url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "id_token",
        "scope": "openid email profile",
        "nonce": str(hash(str(st.session_state))),
    })

    # Render a styled Google button using Streamlit markdown + link
    st.markdown(f"""
    <a href="{oauth_url}" target="_self" style="
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.6rem;
        width: 100%;
        padding: 0.75rem 1.5rem;
        background: white;
        border: 1.5px solid #dadce0;
        border-radius: 12px;
        font-size: 0.95rem;
        font-weight: 500;
        color: #3c4043;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        box-sizing: border-box;
    " onmouseover="this.style.background='#f8f9fa';this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'"
       onmouseout="this.style.background='white';this.style.boxShadow='none'">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
             width="20" height="20" alt="Google">
        Đăng nhập với Google
    </a>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────
#  Main app (after auth)
# ──────────────────────────────────────────────

def main():
    """Main application entry point."""
    _init_session_state()

    # Handle Google OAuth callback — id_token comes in URL fragment (#)
    # This JS extracts it and converts to a query param Streamlit can read
    st.markdown("""
    <script>
        (function() {
            if (window.location.hash) {
                var params = new URLSearchParams(window.location.hash.substring(1));
                var idToken = params.get('id_token');
                if (idToken) {
                    window.location.href = window.location.pathname + '?google_token=' + encodeURIComponent(idToken);
                }
            }
        })();
    </script>
    """, unsafe_allow_html=True)

    # Check authentication
    if not st.session_state.authenticated:
        _render_auth_page()
        return

    # --- Header ---
    st.markdown("""
    <div class="app-header">
        <h1>🔬 AI SOTA Radar</h1>
        <p>Personalized Research Paper Tracker — Find the most relevant papers for your research</p>
    </div>
    """, unsafe_allow_html=True)

    # --- Sidebar ---
    with st.sidebar:
        # User info bar
        user_email = st.session_state.user_email or "User"
        display_name = st.session_state.display_name or user_email.split("@")[0]
        initial = display_name[0].upper() if display_name else "U"

        st.markdown(f"""
        <div class="user-bar">
            <div class="user-avatar">{initial}</div>
            <div>
                <div class="user-email">{display_name}</div>
                <div class="user-label">{user_email}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Đăng xuất", use_container_width=True):
            _clear_user_session()
            st.rerun()

        st.divider()

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
    user_name = st.session_state.display_name or st.session_state.user_email or "Researcher"
    if "@" in user_name:
        user_name = user_name.split("@")[0]

    st.markdown(f"""
    <div style="text-align: center; padding: 3rem 1rem;">
        <h2 style="color: #4f46e5;">Xin chào, {user_name}! 👋</h2>
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
