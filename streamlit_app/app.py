"""
LibraryOS — Streamlit Frontend
Main application entry point with authentication and navigation.
"""

import streamlit as st
from api_client import APIClient

# ── Page Config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="LibraryOS — Intelligent Library Management",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Import Google Fonts ────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Root Variables ─────────────────────────────────────────────────── */
    :root {
        --bg-primary: #0a0a0f;
        --bg-card: rgba(255,255,255,0.04);
        --bg-card-hover: rgba(255,255,255,0.07);
        --border-subtle: rgba(255,255,255,0.08);
        --text-primary: #f1f5f9;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --accent-indigo: #818cf8;
        --accent-purple: #a78bfa;
        --accent-emerald: #34d399;
        --accent-amber: #fbbf24;
        --accent-red: #f87171;
        --gradient-brand: linear-gradient(135deg, #6366f1, #a855f7);
        --radius-lg: 16px;
        --radius-md: 12px;
        --radius-sm: 8px;
    }

    /* ── Base ───────────────────────────────────────────────────────────── */
    html, body, .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        background-color: var(--bg-primary) !important;
        color: var(--text-primary) !important;
    }

    /* ── Sidebar ───────────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d0d1a 0%, #0a0a14 100%) !important;
        border-right: 1px solid var(--border-subtle) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
        font-size: 14px !important;
    }

    /* ── Hide Streamlit Defaults ───────────────────────────────────────── */
    #MainMenu, footer, header {visibility: hidden;}
    .stDeployButton {display: none !important;}

    /* ── Typography ────────────────────────────────────────────────────── */
    h1 {
        font-size: 32px !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px !important;
        color: var(--text-primary) !important;
        margin-bottom: 4px !important;
        line-height: 1.2 !important;
    }
    h2 {
        font-size: 24px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        margin-bottom: 4px !important;
        line-height: 1.3 !important;
    }
    h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
        margin-bottom: 4px !important;
        line-height: 1.4 !important;
    }
    h4 {
        font-size: 15px !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        line-height: 1.4 !important;
    }
    p, li, span, div {
        font-size: 14px !important;
        line-height: 1.6 !important;
    }
    small, .caption-text {
        font-size: 12px !important;
        color: var(--text-muted) !important;
    }

    /* ── Metric Cards ──────────────────────────────────────────────────── */
    [data-testid="stMetric"] {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 20px 24px !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stMetric"]:hover {
        background: var(--bg-card-hover) !important;
        border-color: rgba(99,102,241,0.25) !important;
        transform: translateY(-1px);
    }
    [data-testid="stMetricLabel"] {
        color: var(--text-muted) !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
    }

    /* ── Buttons ────────────────────────────────────────────────────────── */
    .stButton > button {
        background: var(--gradient-brand) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        letter-spacing: 0.2px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 14px rgba(99,102,241,0.25) !important;
    }
    .stButton > button:hover {
        opacity: 0.9 !important;
        box-shadow: 0 6px 20px rgba(99,102,241,0.35) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Secondary Buttons ────────────────────────────────────────────── */
    .stDownloadButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        background: var(--gradient-brand) !important;
        color: white !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* ── Text Inputs / Selects ─────────────────────────────────────────── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div,
    .stNumberInput > div > div > input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        font-size: 14px !important;
    }
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: rgba(99,102,241,0.5) !important;
        box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
    }
    .stTextInput label, .stTextArea label, .stSelectbox label, .stNumberInput label {
        color: var(--text-secondary) !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    /* ── Tabs ──────────────────────────────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background: transparent !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        padding-bottom: 0 !important;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        color: var(--text-muted) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        padding: 10px 20px !important;
        border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
        border-bottom: 2px solid transparent !important;
        transition: all 0.2s ease !important;
    }
    .stTabs [aria-selected="true"] {
        color: var(--accent-indigo) !important;
        border-bottom: 2px solid var(--accent-indigo) !important;
        background: rgba(99,102,241,0.06) !important;
    }

    /* ── Expander ──────────────────────────────────────────────────────── */
    .streamlit-expanderHeader {
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        color: var(--text-primary) !important;
    }

    /* ── Dataframe ─────────────────────────────────────────────────────── */
    .stDataFrame {
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        overflow: hidden !important;
    }

    /* ── Cards (custom class via markdown) ─────────────────────────────── */
    .glass-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 24px;
        margin-bottom: 16px;
        transition: all 0.2s ease;
    }
    .glass-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(99,102,241,0.2);
    }

    /* ── Status Badges ─────────────────────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-active { background: rgba(52,211,153,0.12); color: #34d399; }
    .badge-overdue { background: rgba(248,113,113,0.12); color: #f87171; }
    .badge-returned { background: rgba(148,163,184,0.12); color: #94a3b8; }
    .badge-pending { background: rgba(251,191,36,0.12); color: #fbbf24; }
    .badge-paid { background: rgba(52,211,153,0.12); color: #34d399; }
    .badge-available { background: rgba(52,211,153,0.12); color: #34d399; }
    .badge-borrowed { background: rgba(251,191,36,0.12); color: #fbbf24; }

    /* ── Gradient Text ─────────────────────────────────────────────────── */
    .gradient-text {
        background: linear-gradient(135deg, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    /* ── Book Cards Grid ───────────────────────────────────────────────── */
    .book-card {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: var(--radius-lg);
        padding: 20px;
        transition: all 0.25s ease;
        cursor: pointer;
        height: 100%;
    }
    .book-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(99,102,241,0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.3);
    }

    /* ── Chat Messages ─────────────────────────────────────────────────── */
    .chat-user {
        background: rgba(99,102,241,0.12);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px 16px 4px 16px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.6;
        color: var(--text-primary);
    }
    .chat-bot {
        background: var(--bg-card);
        border: 1px solid var(--border-subtle);
        border-radius: 16px 16px 16px 4px;
        padding: 14px 18px;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.6;
        color: var(--text-primary);
    }

    /* ── Star Rating ───────────────────────────────────────────────────── */
    .star-filled { color: #fbbf24; }
    .star-empty { color: #374151; }

    /* ── Divider ───────────────────────────────────────────────────────── */
    hr {
        border: none !important;
        border-top: 1px solid var(--border-subtle) !important;
        margin: 20px 0 !important;
    }

    /* ── Columns gap adjustment ────────────────────────────────────────── */
    [data-testid="stHorizontalBlock"] {
        gap: 16px !important;
    }

    /* ── Progress bar ──────────────────────────────────────────────────── */
    .stProgress > div > div > div {
        background: var(--gradient-brand) !important;
    }

    /* ── Toast / Alert ─────────────────────────────────────────────────── */
    .stAlert {
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-subtle) !important;
        font-size: 14px !important;
    }

    /* ── Checkbox ───────────────────────────────────────────────────────── */
    .stCheckbox label span {
        font-size: 14px !important;
        color: var(--text-secondary) !important;
    }

    /* ── Container padding ─────────────────────────────────────────────── */
    .block-container {
        padding: 2rem 3rem !important;
        max-width: 1400px !important;
    }

    /* ── Plotly chart background ────────────────────────────────────────── */
    .js-plotly-plot .plotly .main-svg {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Session State Initialization ──────────────────────────────────────────────
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "authenticated": False,
        "token": None,
        "user": None,
        "current_page": "dashboard",
        "chat_history": [],
        "selected_book_id": None,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


init_session_state()


# ── API Client ────────────────────────────────────────────────────────────────
@st.cache_resource
def get_api_client():
    return APIClient()


api = get_api_client()

# Restore token if already authenticated
if st.session_state.token:
    api.set_token(st.session_state.token)


# ── Helper Functions ──────────────────────────────────────────────────────────
def is_librarian() -> bool:
    """Check if current user is librarian or admin."""
    user = st.session_state.get("user")
    if user:
        return user.get("role") in ("LIBRARIAN", "ADMIN")
    return False


def do_logout():
    """Clear session and logout."""
    st.session_state.authenticated = False
    st.session_state.token = None
    st.session_state.user = None
    st.session_state.chat_history = []
    st.session_state.selected_book_id = None
    api.clear_token()


def render_badge(status: str) -> str:
    """Return HTML badge for a status string."""
    css_class = {
        "ACTIVE": "badge-active",
        "OVERDUE": "badge-overdue",
        "RETURNED": "badge-returned",
        "PENDING": "badge-pending",
        "PAID": "badge-paid",
        "WAIVED": "badge-active",
        "AVAILABLE": "badge-available",
        "BORROWED": "badge-borrowed",
        "RESERVED": "badge-pending",
    }.get(status, "badge-pending")
    return f'<span class="badge {css_class}">{status}</span>'


def render_stars(rating: float, max_stars: int = 5) -> str:
    """Return HTML star rating."""
    filled = int(round(rating))
    stars = ""
    for i in range(max_stars):
        cls = "star-filled" if i < filled else "star-empty"
        stars += f'<span class="{cls}" style="font-size:16px;">★</span>'
    return stars


# ── Login Page ────────────────────────────────────────────────────────────────
def render_login_page():
    """Render the login / registration page."""
    # Center the form
    col_left, col_center, col_right = st.columns([1, 1.2, 1])

    with col_left:
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("""
        <div style="text-align:center; padding: 40px 20px;">
            <div style="font-size: 56px; margin-bottom: 16px;">📚</div>
            <h1 style="font-size: 42px !important; margin-bottom: 8px !important;">
                <span class="gradient-text">LibraryOS</span>
            </h1>
            <p style="color: #94a3b8; font-size: 16px !important; line-height: 1.7 !important; max-width: 360px; margin: 0 auto;">
                Intelligent Library Management with Entity Graph &amp; AI-Powered Assistant
            </p>
            <div style="display: flex; gap: 16px; justify-content: center; margin-top: 32px;">
                <div class="glass-card" style="padding: 16px 24px; text-align: center; min-width: 90px;">
                    <div style="font-size: 22px !important; font-weight: 700; color: #818cf8;">20+</div>
                    <div style="font-size: 11px !important; color: #64748b; margin-top: 4px;">Books</div>
                </div>
                <div class="glass-card" style="padding: 16px 24px; text-align: center; min-width: 90px;">
                    <div style="font-size: 22px !important;">🤖</div>
                    <div style="font-size: 11px !important; color: #64748b; margin-top: 4px;">AI Agent</div>
                </div>
                <div class="glass-card" style="padding: 16px 24px; text-align: center; min-width: 90px;">
                    <div style="font-size: 22px !important;">🕸️</div>
                    <div style="font-size: 11px !important; color: #64748b; margin-top: 4px;">Graph</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_center:
        st.markdown("")
        st.markdown("")
        st.markdown("")

        # Toggle between Login and Register
        if "auth_mode" not in st.session_state:
            st.session_state.auth_mode = "login"

        mode = st.session_state.auth_mode

        st.markdown(f"""
        <div class="glass-card" style="padding: 32px;">
            <h2 style="text-align: center; margin-bottom: 4px !important;">
                {"🔑 Welcome Back" if mode == "login" else "✨ Create Account"}
            </h2>
            <p style="text-align: center; color: #64748b; font-size: 13px !important; margin-bottom: 24px;">
                {"Sign in to your library account" if mode == "login" else "Join the university library"}
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.form("auth_form", clear_on_submit=False):
            if mode == "register":
                name = st.text_input("Full Name", placeholder="Enter your full name")

            email = st.text_input("Email Address", placeholder="you@university.edu")
            password = st.text_input("Password", type="password", placeholder="Enter password")

            if mode == "register":
                student_id = st.text_input("Student ID (optional)", placeholder="e.g. STU-2024-001")

            submitted = st.form_submit_button(
                "Sign In" if mode == "login" else "Create Account",
                use_container_width=True,
            )

            if submitted:
                if not email or not password:
                    st.error("Please fill in all required fields.")
                else:
                    try:
                        if mode == "login":
                            result = api.login(email, password)
                        else:
                            result = api.register(
                                name=name,
                                email=email,
                                password=password,
                                student_id=student_id if student_id else None,
                            )

                        # Store auth data
                        st.session_state.token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        api.set_token(result["access_token"])
                        st.success("Welcome!" if mode == "login" else "Account created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"⚠️ {str(e)}")

        # Toggle link
        if mode == "login":
            st.markdown("""<p style="text-align:center; margin-top: 16px;">
                <span style="color: #64748b; font-size: 13px !important;">Don't have an account?</span>
            </p>""", unsafe_allow_html=True)
            if st.button("Register here", use_container_width=True):
                st.session_state.auth_mode = "register"
                st.rerun()
        else:
            st.markdown("""<p style="text-align:center; margin-top: 16px;">
                <span style="color: #64748b; font-size: 13px !important;">Already have an account?</span>
            </p>""", unsafe_allow_html=True)
            if st.button("Sign in here", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()

        # Quick Login buttons
        if mode == "login":
            st.markdown("---")
            st.markdown('<p style="text-align:center; color: #64748b; font-size: 12px !important; margin-bottom: 12px;">⚡ Quick Login</p>', unsafe_allow_html=True)
            q1, q2, q3 = st.columns(3)
            with q1:
                if st.button("👑 Admin", use_container_width=True, key="quick_admin"):
                    try:
                        result = api.login("admin@library.edu", "admin123")
                        st.session_state.token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        api.set_token(result["access_token"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with q2:
                if st.button("📋 Librarian", use_container_width=True, key="quick_librarian"):
                    try:
                        result = api.login("sarah@library.edu", "librarian123")
                        st.session_state.token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        api.set_token(result["access_token"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))
            with q3:
                if st.button("🎓 Student", use_container_width=True, key="quick_student"):
                    try:
                        result = api.login("vishnu@university.edu", "student123")
                        st.session_state.token = result["access_token"]
                        st.session_state.user = result["user"]
                        st.session_state.authenticated = True
                        api.set_token(result["access_token"])
                        st.rerun()
                    except Exception as e:
                        st.error(str(e))


# ── Import Pages ──────────────────────────────────────────────────────────────
from views import dashboard, books, book_detail, circulation, fines, graph_view, agent_chat


# ── Sidebar Navigation ───────────────────────────────────────────────────────
def render_sidebar():
    """Render the sidebar with navigation and user info."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center; padding: 20px 0 24px 0;">
            <div style="font-size: 36px; margin-bottom: 8px;">📚</div>
            <h2 style="font-size: 22px !important; margin: 0 !important;">
                <span class="gradient-text">LibraryOS</span>
            </h2>
            <p style="color: #475569; font-size: 11px !important; margin-top: 4px;">
                Intelligent Library System
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")

        # User info
        user = st.session_state.user
        role_emoji = {"ADMIN": "👑", "LIBRARIAN": "📋", "STUDENT": "🎓"}.get(user.get("role", ""), "👤")
        st.markdown(f"""
        <div class="glass-card" style="padding: 14px 18px; margin-bottom: 20px;">
            <div style="font-size: 14px !important; font-weight: 600; color: #f1f5f9;">
                {role_emoji} {user.get("name", "User")}
            </div>
            <div style="font-size: 12px !important; color: #64748b; margin-top: 2px;">
                {user.get("email", "")}
            </div>
            <div style="margin-top: 6px;">
                <span class="badge badge-active" style="font-size: 10px !important;">{user.get("role", "STUDENT")}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        st.markdown('<p style="font-size: 11px !important; color: #475569; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Navigation</p>', unsafe_allow_html=True)

        nav_items = [
            ("📊", "Dashboard", "dashboard"),
            ("📚", "Book Catalogue", "books"),
            ("🔄", "Circulation", "circulation"),
            ("💰", "Fines", "fines"),
            ("🕸️", "Entity Graph", "graph"),
            ("🤖", "LibraryAI", "agent"),
        ]

        for emoji, label, page_id in nav_items:
            is_active = st.session_state.current_page == page_id
            if st.button(
                f"{emoji}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if is_active else "secondary",
            ):
                st.session_state.current_page = page_id
                st.session_state.selected_book_id = None
                st.rerun()

        st.markdown("---")

        # Logout
        if st.button("🚪  Sign Out", use_container_width=True, key="logout_btn"):
            do_logout()
            st.rerun()

        st.markdown("""
        <div style="position: fixed; bottom: 16px; padding: 0 20px;">
            <p style="font-size: 11px !important; color: #374151;">
                LibraryOS v1.0 · © 2024
            </p>
        </div>
        """, unsafe_allow_html=True)


# ── Main Router ───────────────────────────────────────────────────────────────
def main():
    """Main application entry point."""
    if not st.session_state.authenticated:
        render_login_page()
        return

    render_sidebar()

    # Route to the current page
    page = st.session_state.current_page

    if page == "dashboard":
        dashboard.render(api, is_librarian())
    elif page == "books":
        if st.session_state.selected_book_id:
            book_detail.render(api, st.session_state.selected_book_id)
        else:
            books.render(api)
    elif page == "book_detail":
        book_detail.render(api, st.session_state.selected_book_id)
    elif page == "circulation":
        circulation.render(api, is_librarian())
    elif page == "fines":
        fines.render(api, is_librarian())
    elif page == "graph":
        graph_view.render(api)
    elif page == "agent":
        agent_chat.render(api)
    else:
        dashboard.render(api, is_librarian())


if __name__ == "__main__":
    main()
