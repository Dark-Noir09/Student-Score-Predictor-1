import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px
import base64
from io import BytesIO

# Import custom modules
from database import init_database, save_prediction, get_user_predictions
from auth import init_session_state, login_page, register_page, admin_panel
from report_generator import generate_pdf_report

# Initialize
init_database()
init_session_state()

# Page config
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dark/Light Mode Toggle

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# Dynamic CSS based on mode
if st.session_state.dark_mode:
    css_style = """
        <style>

        header[data-testid="stHeader"] {
            background: rgba(0,0,0,0);
            height: 0rem;
        }

        .main .block-container {
            padding-top: 0rem;
        }

        section.main > div {
            padding-top: 0rem;
        }

        .stApp {
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }

        .main-header {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            padding: 2rem;
            border-radius: 20px;
            color: #0a0a0a;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 0 20px rgba(0,255,136,0.3);
        }

        .prediction-card {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            padding: 2rem;
            border-radius: 20px;
            color: #0a0a0a;
            text-align: center;
            box-shadow: 0 0 30px rgba(0,255,136,0.4);
            margin: 1rem 0;
        }

        .input-section {
            background: #1a1a1a;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.3);
            margin: 1rem 0;
            border: 1px solid #00ff88;
            width: 100%;
        }

        .info-box {
            background: #1a1a1a;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #00ff88;
            color: #00ff88;
        }

        .stMarkdown,
        .stText,
        .stNumberInput label,
        .stSelectbox label,
        .stSlider label {
            color: #00ff88 !important;
            font-size: 20px !important;
            font-weight: 700 !important;
        }

        h1, h2, h3, h4, h5, h6 {
            color: #00ff88 !important;
        }

        p, span, div {
            color: #e0e0e0 !important;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0a0a0a 0%, #1a1a1a 100%);
            border-right: 1px solid #00ff88;
        }

        [data-testid="stSidebar"] * {
            color: #00ff88 !important;
        }

        .stButton > button {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            color: #0a0a0a !important;
            border: none;
            padding: 0.75rem;
            font-weight: bold;
            border-radius: 10px;
            font-size: 18px;
        }

        .stSlider [role="slider"] {
            background-color: #00ff88 !important;
            border: 3px solid white !important;
        }

        .stSlider [data-testid="stTickBar"] {
            background: #00ff88 !important;
            height: 8px !important;
            border-radius: 10px;
        }

        .stSlider span {
            color: #00ff88 !important;
            font-weight: bold !important;
            font-size: 18px !important;
        }

        </style>
    """
else:
    css_style = """
        <style>

        header[data-testid="stHeader"] {
            background: rgba(0,0,0,0);
            height: 0rem;
        }

        .main .block-container {
            padding-top: 0rem;
        }

        section.main > div {
            padding-top: 0rem;
        }

        .stApp {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }

        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }

        .prediction-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin: 1rem 0;
        }

        .input-section {
            background: white;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            margin: 1rem 0;
            width: 100%;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        [data-testid="stSidebar"] * {
            color: white !important;
        }

        .stMarkdown,
        .stText,
        .stNumberInput label,
        .stSelectbox label,
        .stSlider label {
            font-size: 20px !important;
            font-weight: 700 !important;
            color: #222 !important;
        }

        .stButton > button {
            background: linear-gradient(135deg,#667eea,#764ba2);
            color: white !important;
            border: none;
            font-weight: bold;
            border-radius: 12px;
            font-size: 18px;
        }

        .stSlider [role="slider"] {
            background-color: #6c63ff !important;
            border: 3px solid white !important;
        }

        .stSlider div[data-testid="stTickBar"] {
            background: linear-gradient(to right,#667eea,#764ba2) !important;
            height: 8px !important;
            border-radius: 10px;
        }

        .stSlider span {
            color: black !important;
            font-size: 18px !important;
            font-weight: bold !important;
        }

        </style>
    """

st.markdown(css_style, unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        return model, columns
    except FileNotFoundError:
        st.error("❌ Model files not found!")
        st.stop()

# Logo function

def show_logo(width=180):
    try:
        col1, col2, col3 = st.columns([1,2,1])

        with col2:
            st.image("logo.png", width=width)

    except:
        st.markdown("<h1 style='text-align:center;font-size:3rem;'>🎓</h1>", unsafe_allow_html=True)

# Check login status
if not st.session_state.logged_in:

    show_logo(180)

    if st.session_state.page == 'login':
        login_page()
    else:
        register_page()

    st.stop()

# Admin panel
if st.session_state.user['role'] == 'admin':
    admin_panel()
    st.stop()

# Load model for students
model, model_columns = load_model()

# Sidebar
with st.sidebar:

    col_s1, col_s2, col_s3 = st.columns([1,2,1])

    with col_s2:
        st.image("logo.png", width=120)

    st.markdown("## 👤 Student Profile")
    st.markdown(f"**Name:** {st.session_state.user['full_name']}")
    st.markdown(f"**🏫 School:** {st.session_state.user['school_name']}")

    if st.session_state.user.get('grade'):
        st.markdown(f"**📚 Grade:** {st.session_state.user['grade']}")

    if st.session_state.user.get('email'):
        st.markdown(f"**📧 Email:** {st.session_state.user['email']}")

    st.markdown("---")

    col_d1, col_d2 = st.columns([3, 1])

    with col_d1:
        st.markdown("**🌓 Theme Mode**")

    with col_d2:
        if st.button("🌙/☀️", key="theme_toggle"):
            toggle_dark_mode()
            st.rerun()

    st.markdown("---")

    user_pred_df = get_user_predictions(st.session_state.user['id'])

    if not user_pred_df.empty:
        st.markdown("### 📊 Your Statistics")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Predictions", len(user_pred_df))

        with col2:
            avg_score = user_pred_df['predicted_score'].mean()
            st.metric("Average Score", f"{avg_score:.0f}")

    st.markdown("---")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# Main content
st.markdown(f"""
<div class="main-header">

    <div style="display:flex;justify-content:center;margin-bottom:15px;">
        <img src="https://cdn-icons-png.flaticon.com/512/3135/3135755.png"
             width="90">
    </div>

    <h1 style="font-size:55px; color:white;">
        Welcome, {st.session_state.user['full_name']}!
    </h1>

    <p style="font-size:22px; color:white;">
        Predict your exam score and get personalized recommendations to improve
    </p>

</div>
""", unsafe_allow_html=True)

# KEEP YOUR REMAINING ORIGINAL CODE BELOW THIS LINE
# (prediction form, model prediction, charts, tabs, recommendations, report generation etc.)
