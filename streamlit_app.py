import os
import tempfile

import streamlit as st
import matplotlib.pyplot as plt

from backend import MultiDocRAGBot, MAX_FILES

# ==========================================
# PAGE CONFIG & STYLING
# ==========================================
st.set_page_config(page_title="Multi-Source RAG Analyzer", page_icon="📊", layout="wide")

st.markdown(
    """
    <style>
    .stApp {background-color: #0b0f19; color: white;}
    .title-bar {background-color: #1e293b; padding: 20px; border-radius: 10px;
                text-align: center; margin-bottom: 20px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ==========================================
# SESSION STATE (persists across reruns/questions)
# ==========================================
if "bot" not in st.session_state:
    st.session_state.bot = MultiDocRAGBot()
if "messages" not in st.session_state:
    st.session_state.messages = []
if "status" not in st.session_state:
    st.session_state.status = "Waiting..."
if "context_preview" not in st.session_state:
    st.session_state.context_preview = ""
if "last_scores" not in st.session_state:
    st.session_state.last_scores = None

# ==========================================
# HEADER
# ==========================================
st.markdown(
    """
    <div class="title-bar">
        <h1>Multi-Source RAG Analyzer</h1>
        <h3>An intelligent tool that reads your PDFs to provide accurate, source-cited answers with visualization. (Using LangChain)</h3>
        <p>Upload documents up to 5, process them, then chat. (By Nitish Rajak)</p>
    </div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns([1, 2])

# ==========================================
# LEFT PANEL — CONFIG + DEBUGGER
# ==========================================
with left:
    st.subheader("🛠️ Configuration")
    uploaded_files = st.file_uploader(
        "Upload PDFs", type=["pdf", "txt"], accept_multiple_files=True
    )

    col1, col2 = st.columns(2)
    with col1:
        process_clicked = st.button("🚀 Process Documents", use_container_width=True)
    with col2:
        restart_clicked = st.button("🔄 Clear & Restart", use_container_width=True)

    if process_clicked:
        if uploaded_files:
            if len(uploaded_files) > MAX_FILES:
                st.session_state.status = f"⚠️ Status: Error. Max {MAX_FILES} files allowed."
            else:
                with st.spinner("Processing documents..."):
                    temp_dir = tempfile.mkdtemp()
                    temp_paths = []
                    for f in uploaded_files:
                        path = os.path.join(temp_dir, f.name)
                        with open(path, "wb") as out:
                            out.write(f.getbuffer())
                        temp_paths.append(path)
                    st.session_state.status = st.session_state.bot.process_files(temp_paths)
        else:
            st.session_state.status = "⚠️ Status: No file uploaded."

    if restart_clicked:
        st.session_state.bot = MultiDocRAGBot()
        st.session_state.messages = []
        st.session_state.status = "✅ Cleared—upload new files to start fresh!"
        st.session_state.context_preview = ""
        st.session_state.last_scores = None
        st.rerun()

    st.text_input("Status", value=st.session_state.status, disabled=True, label_visibility="collapsed")

    st.subheader("🔍 Live Debugger")
    st.text_area(
        "Retrieved Chunks",
        value=st.session_state.context_preview,
        height=400,
        disabled=True,
        label_visibility="collapsed",
    )

# ==========================================
# RIGHT PANEL — CHAT
# ==========================================
with right:
    st.subheader("💬 AI Assistant")

    chat_box = st.container(height=550)
    with chat_box:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    user_input = st.chat_input("Ask your question here...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner("Thinking..."):
            reply, context_preview, docs_and_scores = st.session_state.bot.ask(user_input)
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.session_state.context_preview = context_preview
        st.session_state.last_scores = docs_and_scores
        st.rerun()

# ==========================================
# ANALYTICS DASHBOARD
# ==========================================
st.subheader("📊 Analytics Dashboard")
plot_col1, plot_col2 = st.columns(2)

if st.session_state.last_scores:
    scores = [score for doc, score in st.session_state.last_scores]
    sources = [doc.metadata.get("source_id", "Unknown") for doc, score in st.session_state.last_scores]

    with plot_col1:
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        fig1.patch.set_facecolor("#0b0f19")
        ax1.set_facecolor("#0b0f19")
        bar_colors = ["#3b82f6", "#22d3ee", "#34d399", "#facc15", "#fb923c"]
        if len(scores) > len(bar_colors):
            bar_colors = bar_colors * (len(scores) // len(bar_colors) + 1)
        ax1.bar(range(1, len(scores) + 1), scores, color=bar_colors[: len(scores)])
        ax1.set_xlabel("Chunk Rank", color="white")
        ax1.set_ylabel("Distance (Lower is Better)", color="white")
        ax1.set_title("Relevance Score", color="white", fontweight="bold")
        ax1.tick_params(colors="white")
        ax1.grid(axis="y", linestyle="--", alpha=0.3)
        st.pyplot(fig1)

    with plot_col2:
        source_counts = {}
        for s in sources:
            source_counts[s] = source_counts.get(s, 0) + 1
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        fig2.patch.set_facecolor("#0b0f19")
        pie_colors = ["#4ade80", "#f472b6", "#60a5fa"]
        ax2.pie(
            source_counts.values(),
            labels=source_counts.keys(),
            autopct="%1.1f%%",
            colors=pie_colors,
            textprops={"color": "white"},
        )
        ax2.set_title("Source Distribution", color="white", fontweight="bold")
        st.pyplot(fig2)
else:
    with plot_col1:
        st.info("Ask a question to see the relevance score chart.")
    with plot_col2:
        st.info("Ask a question to see the source distribution chart.")
