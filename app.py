import streamlit as st
from PIL import Image
from utils import extract_transactions_from_pdf

# --- Page Configuration ---
st.set_page_config(page_title="Global IME Bank - Statement Analyzer", page_icon="🏦", layout="wide")

# --- Custom Styling ---
st.markdown("<style>div.block-container{padding-top:1rem;}</style>", unsafe_allow_html=True)

# --- Hide Sidebar ---
hide_sidebar_style = """
    <style>
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stSidebarNav"] {
            display: none;
        }
    </style>
"""
st.markdown(hide_sidebar_style, unsafe_allow_html=True)

# --- Logo & Title ---
image = Image.open("logo.png")
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.markdown("<div style='margin-top:-100px'></div>", unsafe_allow_html=True)
    st.image(image, width=0)
with col2:
    st.markdown("""
        <style>.title-test { margin-top: 100px; padding: 5px; border-radius: 6px; }</style>
        <center><h2 class="title-test">Global IME Bank Statement Analyzer</h2></center>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- Upload Area ---
st.markdown("""
    <div style='text-align: center;'>
        <h3>📁 Upload PDF</h3>
        <p>Drag and drop your bank statement here (PDF only)</p>
    </div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_pdf = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

# --- File Handling ---
if uploaded_pdf:
    with st.spinner("🔍 Extracting transactions..."):
        try:
            df, holder, start, end = extract_transactions_from_pdf(uploaded_pdf)

            if df.empty or not holder or not start or not end:
                raise ValueError("Incomplete data extracted.")

            # Save to session state
            st.session_state.df = df
            st.session_state.holder = holder
            st.session_state.start = start
            st.session_state.end = end

            st.success("✅ Transactions extracted successfully! Redirecting...")
            st.switch_page("pages/analyze.py")

        except Exception as e:
            # Clear previous session state (if any)
            for key in ["df", "holder", "start", "end"]:
                st.session_state.pop(key, None)

            st.error(f"❌ Failed to process the PDF. Please ensure it's a valid Global IME bank statement.\n\n**Error:** {str(e)}")
else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("📄 Please upload a bank statement PDF.")
