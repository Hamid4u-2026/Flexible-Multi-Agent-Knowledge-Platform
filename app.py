import streamlit as st
from pipeline_core import run_unified_pipeline

# ==========================================
# Page Configuration
# ==========================================
st.set_page_config(
    page_title="Academic Guidance Portal",
    page_icon="\U0001F393",
    layout="wide"
)

# ==========================================
# Session State
# ==========================================
if "recent_queries" not in st.session_state:
    st.session_state.recent_queries = []

if "active_result" not in st.session_state:
    st.session_state.active_result = None

if "active_query" not in st.session_state:
    st.session_state.active_query = ""

# ==========================================
# Minimal Professional Styling
# ==========================================
st.markdown("""
<style>
.main-header {
    font-size: 2.1rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 2px;
}

.sub-header {
    font-size: 2.1rem;
    font-weight: 700;
    color: #1E3A8A;
    margin-bottom: 18px;
}

.status-card {
    background-color: #F8FAFC;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px 15px;
    margin-bottom: 10px;
}

.status-label {
    font-weight: 600;
    color: #64748B;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 3px;
}

.status-value {
    font-size: 1rem;
    font-weight: 700;
    color: #0F172A;
}

.abstain-box {
    background-color: #FEF2F2;
    border: 1px solid #FCA5A5;
    border-radius: 8px;
    padding: 16px;
    color: #991B1B;
    margin-bottom: 12px;
}

.recent-card {
    background-color: #F8FAFC;
    color: #0F172A;
    border: 1px solid #E2E8F0;
    border-radius: 8px;
    padding: 12px;
    min-height: 90px;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# Header
# ==========================================
st.markdown(
    '<div class="sub-header">Syrian Virtual University</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="main-header">Academic Guidance Portal</div>',
    unsafe_allow_html=True
)

# ==========================================
# Academic Query Input
# ==========================================
with st.form(key="academic_query_form"):
    user_query = st.text_input(
        label="",
        value="",
        placeholder="Enter your academic inquiry (A/E)",
        label_visibility="collapsed"
    )

    submit_button = st.form_submit_button(
        label="Enter",
        use_container_width=False
    )

if submit_button and user_query.strip():

    with st.spinner("Agents Processing Query..."):
        result = run_unified_pipeline(user_query)

    st.session_state.active_result = result
    st.session_state.active_query = user_query

    history_item = {
        "query": user_query,
        "result": result
    }

    # Keep only the latest three questions.
    st.session_state.recent_queries = [
        item
        for item in st.session_state.recent_queries
        if item["query"] != user_query
    ]

    st.session_state.recent_queries.insert(0, history_item)
    st.session_state.recent_queries = st.session_state.recent_queries[:3]


# ==========================================
# Current Result
# ==========================================
if st.session_state.active_result:

    result = st.session_state.active_result
    status_info = result.get("status", {})

    answer = result.get("answer", "")
    source = result.get("source", "")

    local_status = status_info.get(
        "Local Retrieval",
        status_info.get(
            "local_retrieval",
            status_info.get("local_retrieval_status", "Sufficient")
        )
    )

    web_status = status_info.get(
        "Web Fallback",
        status_info.get(
            "web_fallback",
            status_info.get("web_fallback_status", "Not Used")
        )
    )

    provider = status_info.get(
        "Generation Provider",
        status_info.get(
            "provider",
            "Groq API \u2014 GPT-OSS 20B"
        )
    )

    # Detect the actual abstention result without changing pipeline logic.
    abstention_texts = [
        "Insufficient evidence found in the available knowledge sources.",
        "The provided knowledge is not sufficient",
        "لا توجد أدلة كافية في مصادرالمعرفة المتاحة."
        
    ]

    is_abstained = any(
        text in answer.strip()
        for text in abstention_texts
    )

    # ==========================================
    # Answer + Status
    # ==========================================
    col_answer, col_status = st.columns(
        [2.7, 1],
        gap="large"
    )

    with col_answer:

        st.subheader("Final Answer")

        if is_abstained:
            st.markdown("""
            <div class="abstain-box">
                <strong>Abstained</strong><br>
                Insufficient evidence found in the available knowledge sources.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.write(answer)

        st.markdown("### Source Attribution")

        if source and source != "N/A":

            if isinstance(source, list):
                for src in source:
                    icon = "\U0001F4C4 "
                    st.markdown(f"{icon}`{src}`")

            else:
                source_lines = [
                    line.strip()
                    for line in str(source).split("\n")
                    if line.strip()
                ]

                for src in source_lines:
                    icon = (
                        "\U0001F4C4 "
                        if "http" in src
                        or "svuonline" in src.lower()
                        else "\U0001F4C4 "
                    )
                    st.markdown(f"{icon}`{src}`")

        else:
            st.caption("N/A - Insufficient Evidence")

    # ==========================================
    # Operational Status
    # ==========================================
    with col_status:

        st.subheader("Pipeline Status")

        if str(local_status).lower() == "sufficient":
            local_badge = "\U0001F7E2 Sufficient"
        elif str(local_status).lower() == "insufficient":
            local_badge = "\U0001F534 Insufficient"
        else:
            local_badge = f"\U0001F534 Insufficient"

        if str(web_status).lower() == "used":
            web_badge = "\U0001F7E2 Used"
        elif str(web_status).lower() == "no evidence":
            web_badge = "\U0001F7E1 No Evidence Found"
        else:
            web_badge = "\U0001F535 Not Used"

        st.markdown(f"""
        <div class="status-card">
            <div class="status-label">Local Retrieval</div>
            <div class="status-value">{local_badge}</div>
        </div>

        <div class="status-card">
            <div class="status-label">Web Fallback</div>
            <div class="status-value">{web_badge}</div>
        </div>

        <div class="status-card">
            <div class="status-label">Generation Provider</div>
            <div class="status-value">\U0001F916 {provider}</div>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# Recent Questions
# ==========================================

st.subheader("Recent Questions")

recent_items = st.session_state.recent_queries[:3]

if recent_items:

    cols = st.columns(len(recent_items))

    numbers = [chr(0x2460), chr(0x2461), chr(0x2462)]

    for idx, item in enumerate(recent_items):

        query_text = item["query"]

        with cols[idx]:

            st.markdown(
                f"""
                <div class="recent-card">
                    <strong>{numbers[idx]} {query_text}</strong>
                </div>
                """,
                unsafe_allow_html=True
            )

            if st.button(
                f"View {numbers[idx]}",
                key=f"view_recent_{idx}",
                use_container_width=True
            ):
                st.session_state.active_query = item["query"]
                st.session_state.active_result = item["result"]
                st.rerun()

else:

    st.caption("No recent questions yet.")
