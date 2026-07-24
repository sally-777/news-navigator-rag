from importlib import import_module
import streamlit as st

# Import core RAG logic
answer_question = import_module("07_prompting").answer_question

# Page configuration
st.set_page_config(
    page_title="SATECK | AI News Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom Creative CSS
st.markdown(
    """
    <style>
    .stApp { background-color: #f8fafc; }
    
    .brand-badge {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        color: white;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
    }
    
    .main-title {
        text-align: center;
        color: #0f172a;
        font-weight: 900;
        font-size: 2.3rem;
        margin-bottom: 0.2rem;
    }
    
    .tagline {
        text-align: center;
        color: #475569;
        font-size: 1.1rem;
        font-weight: 500;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: #ffffff;
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .feature-card h5 { margin: 0; color: #1e293b; font-weight: 700; font-size: 0.95rem; }
    .feature-card p { margin: 3px 0 0 0; color: #64748b; font-size: 0.8rem; }
    </style>
""",
    unsafe_allow_html=True,
)

# Brand Header Section
st.markdown(
    """
    <div style='text-align: center;'>
        <span class='brand-badge'>⚡ SATECK AI PLATFORM</span>
        <h1 class='main-title'>SATECK News Intelligence</h1>
        <p class='tagline'>✨ Instant, Fact-Checked News Summaries & Live Analytics</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Feature Metrics Bar
m_col1, m_col2, m_col3 = st.columns(3)
with m_col1:
    st.markdown(
        """
        <div class='feature-card'>
            <h5>🎯 Verified Sources</h5>
            <p>Directly grounded in authentic news</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

with m_col2:
    st.markdown(
        """
        <div class='feature-card'>
            <h5>🌐 Live Web Connect</h5>
            <p>Real-time API retrieval enabled</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

with m_col3:
    st.markdown(
        """
        <div class='feature-card'>
            <h5>🗣️ Cross-Lingual</h5>
            <p>Ask in Arabic or English seamlessly</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

st.write("")
st.divider()

# Session State for Category Filter
if "category_filter" not in st.session_state:
    st.session_state.category_filter = "All"

# Category Focus Section
st.markdown("##### 📌 Optional Category Focus:")
cat_col1, cat_col2, cat_col3, cat_col4, cat_col5, cat_col6 = st.columns(6)

with cat_col1:
    if st.button("🌐 All Categories", use_container_width=True):
        st.session_state.category_filter = "All"
with cat_col2:
    if st.button("💻 Tech", use_container_width=True):
        st.session_state.category_filter = "Technology"
with cat_col3:
    if st.button("📈 Business", use_container_width=True):
        st.session_state.category_filter = "Business"
with cat_col4:
    if st.button("⚽ Sport", use_container_width=True):
        st.session_state.category_filter = "Sport"
with cat_col5:
    if st.button("🏛️ Politics", use_container_width=True):
        st.session_state.category_filter = "Politics"
with cat_col6:
    if st.button("🎬 Entertainment", use_container_width=True):
        st.session_state.category_filter = "Entertainment"

# Active Filter Hint
if st.session_state.category_filter != "All":
    st.caption(f"🎯 Current Focus Tag: **{st.session_state.category_filter}**")

st.write("")

# Main Search Section using Form (Supports Enter-Key Submission)
st.markdown("##### 🔍 Search & Analyze News:")

with st.form(key="search_form", clear_on_submit=False):
    input_col, lang_col = st.columns([4, 1])

    with lang_col:
        lang_choice = st.selectbox(
            "Response Language:",
            ["Auto-detect", "Arabic (العربية)", "English"],
        )

    with input_col:
        user_query = st.text_input(
            label="Ask anything:",
            placeholder="Type any query (e.g., How do political decisions impact tech stock profits?)...",
            label_visibility="collapsed",
        )

    btn_col, _ = st.columns([1, 4])
    with btn_col:
        submit_btn = st.form_submit_button(
            "🚀 Search Now", use_container_width=True, type="primary"
        )

# Execute Search & Retrieval Logic
if submit_btn and user_query.strip():
    final_query = user_query
    if st.session_state.category_filter != "All":
        final_query += f" (Focus context on {st.session_state.category_filter})"

    if "Arabic" in lang_choice:
        final_query += " (Please respond in Arabic)."
    elif "English" in lang_choice:
        final_query += " (Please respond in English)."

    with st.spinner(
        "⚡ SATECK Engine analyzing multi-source articles & generating insights..."
    ):
        answer, sources, fetched_new_data = answer_question(final_query)

    if fetched_new_data:
        st.toast(
            "SATECK Live API: External web articles fetched & integrated!", icon="🌐"
        )

    st.write("")
    st.markdown("### 📝 AI Generated Intelligence:")
    st.info(answer)

    # Render Sources with Clickable Links and Snippets
    if sources:
        with st.expander("📚 Verified Sources & Citations"):
            for i, src in enumerate(sources, 1):
                title = src.get("title", "News Source")
                url = src.get("url") or src.get("link")

                # Display clickable title if URL exists
                if url and str(url).startswith("http"):
                    st.markdown(f"**[{i}] [{title}]({url})** 🔗")
                else:
                    st.markdown(f"**[{i}] {title}**")

                # Display snippet if text content is available
                snippet = (
                    src.get("text")
                    or src.get("content")
                    or src.get("description")
                    or ""
                )

                if snippet.strip():
                    st.caption(f"📍 Snippet: {snippet[:200]}...")

                st.divider()

elif submit_btn:
    st.warning("Please enter a query first!")