import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

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
        /* Dark Mode Styles */
        .stApp {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        }
        .main-header {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin-bottom: 2rem;
            text-align: center;
        }
        .prediction-card {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            margin: 1rem 0;
        }
        .input-section {
            background: #16213e;
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.2);
            margin: 1rem 0;
            border: 1px solid #00b894;
        }
        .info-box {
            background: #1a1a2e;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #00b894;
            color: #e0e0e0;
        }
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label {
            color: #e0e0e0 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            color: #00b894 !important;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f0f1a 0%, #1a1a2e 100%);
        }
        [data-testid="stSidebar"] * {
            color: #e0e0e0;
        }
        .stButton > button {
            background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            font-weight: bold;
            border-radius: 10px;
        }
        </style>
    """
else:
    css_style = """
        <style>
        /* Light Mode Styles */
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
        }
        .info-box {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            border-left: 4px solid #667eea;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }
        [data-testid="stSidebar"] * {
            color: white;
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

# Check login status
if not st.session_state.logged_in:
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
    st.markdown("## 👤 Student Profile")
    st.markdown(f"**Name:** {st.session_state.user['full_name']}")
    st.markdown(f"**🏫 School:** {st.session_state.user['school_name']}")
    if st.session_state.user.get('grade'):
        st.markdown(f"**📚 Grade:** {st.session_state.user['grade']}")
    if st.session_state.user.get('email'):
        st.markdown(f"**📧 Email:** {st.session_state.user['email']}")
    
    st.markdown("---")
    
    # Dark mode toggle
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.markdown("**🌓 Theme Mode**")
    with col_d2:
        if st.button("🌙/☀️", key="theme_toggle"):
            toggle_dark_mode()
            st.rerun()
    
    st.markdown("---")
    
    # User stats
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
        <h1>🎓 Welcome, {st.session_state.user['full_name']}!</h1>
        <p>Predict your exam score and get personalized recommendations</p>
    </div>
""", unsafe_allow_html=True)

# Simplified Input Form - Only Essential Fields
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center;'>📝 Student Information</h2>", unsafe_allow_html=True)
    
    with st.form("prediction_form"):
        # Academic Information (Essential)
        st.markdown("### 📚 Academic Information")
        col_a, col_b = st.columns(2)
        with col_a:
            hours = st.slider("📖 Hours Studied per Day", 0.0, 24.0, 6.0, 0.5, 
                            help="Recommended: 6-8 hours")
            attendance = st.slider("📅 Attendance Percentage", 0.0, 100.0, 85.0, 5.0,
                                  help="Recommended: 85-100%")
        with col_b:
            previous = st.slider("📊 Previous Exam Score", 0.0, 100.0, 65.0, 5.0)
            sleep = st.slider("😴 Sleep Hours per Night", 0.0, 12.0, 7.0, 0.5,
                            help="Recommended: 7-9 hours")
        
        # Personal Factors (Essential)
        st.markdown("### 💪 Personal Factors")
        col_c, col_d = st.columns(2)
        with col_c:
            motivation = st.selectbox("🎯 Motivation Level", ["Low", "Medium", "High"], index=2)
            teacher = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"], index=2)
        with col_d:
            parent = st.selectbox("👨‍👩‍👧 Parental Involvement", ["Low", "Medium", "High"], index=2)
            peer = st.selectbox("👥 Peer Influence", ["Negative", "Neutral", "Positive"], index=2)
        
        # Environment Factors (Essential)
        st.markdown("### 🏫 Environment Factors")
        col_e, col_f = st.columns(2)
        with col_e:
            school = st.selectbox("🏛️ School Type", ["Public", "Private"], index=1)
            internet = st.selectbox("🌐 Internet Access", ["No", "Yes"], index=1)
        with col_f:
            tutoring = st.selectbox("📚 Tutoring Sessions", [0, 1, 2, 3, 4], index=2)
            activities = st.selectbox("⚽ Extracurricular Activities", ["No", "Yes"], index=1)
        
        st.markdown("---")
        submitted = st.form_submit_button("🎯 Predict My Score", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle prediction
if 'submitted' in locals() and submitted:
    with st.spinner("Analyzing your data..."):
        # Simplified input data (only essential fields)
        input_data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring,
            "Sleep_Hours": sleep,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet,
            "Parental_Involvement": parent,
            "Peer_Influence": peer,
            "Extracurricular_Activities": activities,
        }
        
        # Prepare for model
        data_for_model = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring,
            "Sleep_Hours": sleep,
            "Distance_from_Home": 10,  # Default value
            "Physical_Activity": 3,     # Default value
            "Health": 3,                # Default value
            "Motivation_Level_Low": 1 if motivation == "Low" else 0,
            "Motivation_Level_Medium": 1 if motivation == "Medium" else 0,
            "Teacher_Quality_Good": 1 if teacher == "Good" else 0,
            "Teacher_Quality_Poor": 1 if teacher == "Poor" else 0,
            "School_Type_Public": 1 if school == "Public" else 0,
            "Internet_Access_Yes": 1 if internet == "Yes" else 0,
            "Family_Income_Low": 0,
            "Family_Income_Medium": 0,
            "Parental_Involvement_Low": 1 if parent == "Low" else 0,
            "Parental_Involvement_Medium": 1 if parent == "Medium" else 0,
            "Parental_Education_Level_Postgraduate": 0,
            "Parental_Education_Level_School": 0,
            "Peer_Influence_Neutral": 1 if peer == "Neutral" else 0,
            "Peer_Influence_Positive": 1 if peer == "Positive" else 0,
            "Access_to_Resources_Low": 0,
            "Access_to_Resources_Medium": 0,
            "Extracurricular_Activities_Yes": 1 if activities == "Yes" else 0,
            "Study_Environment_Good": 0,
            "Study_Environment_Poor": 0,
            "Score_Range_60-80": 0,
            "Score_Range_81-90": 0,
            "Score_Range_91-100": 0,
        }
        
        # Create DataFrame and align columns
        input_df = pd.DataFrame([data_for_model])
        for col in model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model_columns]
        
        # Predict
        prediction = model.predict(input_df)[0]
        final_score = max(40, min(100, prediction))
        final_score = int(round(final_score))
        
        # Generate recommendations
        recommendations = []
        if hours < 6:
            recommendations.append("📖 Increase study hours to 6-8 per day")
        if hours > 10:
            recommendations.append("😴 Reduce study hours to avoid burnout")
        if sleep < 7:
            recommendations.append("😴 Get 7-9 hours of sleep for better focus")
        if attendance < 85:
            recommendations.append("🏫 Improve attendance to 85%+")
        if motivation == "Low":
            recommendations.append("🎯 Set daily goals to boost motivation")
        if teacher == "Poor":
            recommendations.append("📚 Seek additional learning resources online")
        if parent == "Low":
            recommendations.append("👨‍👩‍👧 Discuss studies with parents for support")
        if peer == "Negative":
            recommendations.append("👥 Join positive study groups")
        
        if not recommendations:
            recommendations = ["🌟 Great habits! Keep maintaining your routine"]
        
        # Save prediction
        save_prediction(st.session_state.user['id'], st.session_state.user['username'], 
                       input_data, final_score, " | ".join(recommendations[:5]))
        
        # Display prediction
        st.markdown("---")
        st.markdown(f"""
            <div class="prediction-card">
                <h2>🎯 Your Predicted Exam Score</h2>
                <div style="font-size: 4rem; font-weight: bold; margin: 1rem 0;">{final_score}/100</div>
                <p>Based on your study habits and personal factors</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Grade message
        if final_score >= 90:
            grade, color, emoji = "A+", "#4CAF50", "🌟"
            message = "Outstanding! You're in the top tier!"
        elif final_score >= 80:
            grade, color, emoji = "A", "#8BC34A", "🎉"
            message = "Very good! Keep up the momentum!"
        elif final_score >= 70:
            grade, color, emoji = "B", "#FFC107", "📈"
            message = "Good! Consistent effort will improve results"
        elif final_score >= 60:
            grade, color, emoji = "C", "#FF9800", "📚"
            message = "Satisfactory. More focus needed"
        elif final_score >= 50:
            grade, color, emoji = "D", "#FF5722", "⚠️"
            message = "Needs improvement. Consider tutoring"
        else:
            grade, color, emoji = "F", "#f44336", "🔴"
            message = "Critical. Immediate intervention recommended"
        
        st.markdown(f"""
            <div class="info-box" style="text-align: center;">
                <h3 style="color: {color};">{emoji} Grade: {grade}</h3>
                <p>{message}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Recommendations
        st.markdown("### 💡 Personalized Recommendations")
        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"{i}. {rec}")
        
        # Download Report Button
        st.markdown("---")
        if st.button("📥 Download Detailed Report (PDF)", use_container_width=True):
            with st.spinner("Generating your report..."):
                pdf_buffer = generate_pdf_report(
                    st.session_state.user,
                    input_data,
                    final_score,
                    recommendations
                )
                
                st.download_button(
                    label="💾 Click to Save PDF Report",
                    data=pdf_buffer,
                    file_name=f"student_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <p>🎓 Student Score Predictor | Based on Machine Learning Analysis</p>
        <p style="font-size: 0.8rem;">This tool provides predictions based on historical data patterns.</p>
    </div>
""", unsafe_allow_html=True)
