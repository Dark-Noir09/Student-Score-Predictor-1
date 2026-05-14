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
        /* Remove ALL white spaces and default padding */
        #root > div:first-child {
            padding-top: 0 !important;
        }
        .main > div {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        .stApp {
            margin-top: 0px !important;
            padding-top: 0px !important;
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%);
        }
        .main-header {
            background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%);
            padding: 2rem;
            border-radius: 20px;
            color: #0a0a0a;
            margin: 1rem 0;
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
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label {
            color: #00ff88 !important;
            font-size: 16px !important;
            font-weight: 500 !important;
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
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 0 20px rgba(0,255,136,0.5);
        }
        .stSlider label {
            color: #00ff88 !important;
            font-size: 16px !important;
        }
        .stSlider [data-baseweb="slider"] {
            background-color: #00ff88 !important;
        }
        .stSlider [data-testid="stTickBar"] {
            background: #00ff88 !important;
        }
        .stMetric label, .stMetric value {
            color: #00ff88 !important;
        }
        .logo-container {
            text-align: center;
            margin: 1rem 0;
        }
        .stSlider [data-baseweb="slider"] div[role="slider"] {
            background-color: #00ff88 !important;
            border-color: #00ff88 !important;
        }
        .stSlider [data-testid="stThumbValue"] {
            color: #00ff88 !important;
            background: #0a0a0a !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """
else:
    css_style = """
        <style>
        /* Remove ALL white spaces and default padding */
        #root > div:first-child {
            padding-top: 0 !important;
        }
        .main > div {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 1rem !important;
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            max-width: 100% !important;
        }
        header[data-testid="stHeader"] {
            display: none !important;
        }
        [data-testid="stDecoration"] {
            display: none !important;
        }
        [data-testid="stStatusWidget"] {
            display: none !important;
        }
        .stApp {
            margin-top: 0px !important;
            padding-top: 0px !important;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .main-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            color: white;
            margin: 1rem 0;
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
            color: white !important;
        }
        .logo-container {
            text-align: center;
            margin: 1rem 0;
        }
        .stMarkdown, .stText, .stNumberInput label, .stSelectbox label {
            font-size: 16px !important;
            font-weight: 500 !important;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
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
def show_logo():
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=120, use_column_width=False)
    except:
        st.markdown("<h1 style='text-align: center; font-size: 3rem;'>🎓</h1>", unsafe_allow_html=True)

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
    # Centered logo in sidebar
    st.markdown('<div style="text-align: center; padding: 0.5rem 0;">', unsafe_allow_html=True)
    try:
        st.image("logo.png", width=80, use_column_width=False)
    except:
        st.markdown("<h2 style='text-align: center;'>🎓</h2>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
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

# Main content - Logo centered before welcome
st.markdown('<div class="logo-container">', unsafe_allow_html=True)
show_logo()
st.markdown('</div>', unsafe_allow_html=True)

# Welcome header
st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {st.session_state.user['full_name']}!</h1>
        <p>Predict your exam score and get personalized recommendations to improve</p>
    </div>
""", unsafe_allow_html=True)

# Input Form - Full width
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown("<h2 style='text-align: center;'>📝 Student Information</h2>", unsafe_allow_html=True)

with st.form("prediction_form", clear_on_submit=False):
    # Academic Information - All sliders default to 0
    st.markdown("### 📚 Academic Information")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        hours = st.slider("📖 Hours Studied per Day", 0.0, 24.0, 0.0, 0.5, 
                        help="Recommended: 6-8 hours")
    with col_b:
        attendance = st.slider("📅 Attendance Percentage", 0.0, 100.0, 0.0, 5.0,
                              help="Recommended: 85-100%")
    with col_c:
        previous = st.slider("📊 Previous Exam Score", 0.0, 100.0, 0.0, 5.0)
    
    # Personal Factors
    st.markdown("### 💪 Personal Factors")
    col_d, col_e, col_f = st.columns(3)
    with col_d:
        sleep = st.slider("😴 Sleep Hours per Night", 0.0, 12.0, 0.0, 0.5,
                        help="Recommended: 7-9 hours")
        motivation = st.selectbox("🎯 Motivation Level", ["Low", "Medium", "High"], index=0)
    with col_e:
        teacher = st.selectbox("👨‍🏫 Teacher Quality", ["Poor", "Average", "Good"], index=0)
        parent = st.selectbox("👨‍👩‍👧 Parental Involvement", ["Low", "Medium", "High"], index=0)
    with col_f:
        tutoring = st.selectbox("📚 Tutoring Sessions", [0, 1, 2, 3, 4], index=0)
        peer = st.selectbox("👥 Peer Influence", ["Negative", "Neutral", "Positive"], index=0)
    
    # Environment Factors
    st.markdown("### 🏫 Environment Factors")
    col_g, col_h = st.columns(2)
    with col_g:
        school = st.selectbox("🏛️ School Type", ["Public", "Private"], index=0)
        internet = st.selectbox("🌐 Internet Access", ["No", "Yes"], index=0)
    with col_h:
        activities = st.selectbox("⚽ Extracurricular Activities", ["No", "Yes"], index=0)
    
    st.markdown("---")
    submitted = st.form_submit_button("🎯 Predict My Score", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Handle prediction
if 'submitted' in locals() and submitted:
    with st.spinner("Analyzing your data..."):
        # Prepare input data
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
            "Distance_from_Home": 10,
            "Physical_Activity": 3,
            "Health": 3,
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
        if hours < 6 and hours > 0:
            recommendations.append("📖 Increase study hours to 6-8 per day")
        if hours > 10:
            recommendations.append("😴 Reduce study hours to avoid burnout")
        if sleep < 7 and sleep > 0:
            recommendations.append("😴 Get 7-9 hours of sleep for better focus")
        if attendance < 85 and attendance > 0:
            recommendations.append("🏫 Improve attendance to 85%+")
        if motivation == "Low":
            recommendations.append("🎯 Set daily goals to boost motivation")
        if teacher == "Poor":
            recommendations.append("📚 Seek additional learning resources online")
        if parent == "Low":
            recommendations.append("👨‍👩‍👧 Discuss studies with parents for support")
        if peer == "Negative":
            recommendations.append("👥 Join positive study groups")
        if tutoring == 0:
            recommendations.append("📚 Consider tutoring sessions for better understanding")
        
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
            grade, emoji = "A+", "🌟"
            message = "Outstanding! You're in the top tier!"
        elif final_score >= 80:
            grade, emoji = "A", "🎉"
            message = "Very good! Keep up the momentum!"
        elif final_score >= 70:
            grade, emoji = "B", "📈"
            message = "Good! Consistent effort will improve results"
        elif final_score >= 60:
            grade, emoji = "C", "📚"
            message = "Satisfactory. More focus needed"
        elif final_score >= 50:
            grade, emoji = "D", "⚠️"
            message = "Needs improvement. Consider tutoring"
        else:
            grade, emoji = "F", "🔴"
            message = "Critical. Immediate intervention recommended"
        
        # Tabs for detailed analysis
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance Analysis", "💡 Recommendations", "📈 Comparison Chart", "📉 Historical Trend"])
        
        with tab1:
            st.markdown("### 📊 Performance Analysis")
            
            if hours > 0 or attendance > 0 or sleep > 0 or previous > 0:
                fig = go.Figure()
                
                categories = ['Study Hours', 'Attendance', 'Sleep', 'Previous Score', 'Predicted Score']
                values = [hours, attendance, sleep, previous, final_score]
                optimal = [7, 85, 8, 85, 85]
                
                fig.add_trace(go.Bar(name='Your Value', x=categories, y=values, 
                                    marker_color='#00ff88' if st.session_state.dark_mode else '#667eea'))
                fig.add_trace(go.Bar(name='Optimal Range', x=categories, y=optimal, 
                                    marker_color='#ff6b6b', opacity=0.7))
                
                fig.update_layout(
                    title="Your Performance vs Optimal Ranges",
                    xaxis_title="Metrics",
                    yaxis_title="Value",
                    barmode='group',
                    height=450,
                    template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                    paper_bgcolor='rgba(0,0,0,0)' if st.session_state.dark_mode else 'white',
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Enter values above to see performance analysis")
        
        with tab2:
            st.markdown("### 💡 Personalized Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            st.markdown("### 📊 Priority Improvement Areas")
            impacts = []
            if hours < 6 and hours > 0:
                impacts.append(("Low Study Hours", -15, "HIGH", "Increase to 6-8 hours"))
            if hours > 10:
                impacts.append(("Excessive Study", -5, "MEDIUM", "Take more breaks"))
            if attendance < 85 and attendance > 0:
                impacts.append(("Low Attendance", -12, "HIGH", "Improve attendance"))
            if sleep < 7 and sleep > 0:
                impacts.append(("Insufficient Sleep", -8, "HIGH", "Get 7-9 hours sleep"))
            if motivation != "High":
                impacts.append(("Low Motivation", -10, "MEDIUM", "Set daily goals"))
            if teacher != "Good":
                impacts.append(("Teacher Quality", -7, "MEDIUM", "Seek additional resources"))
            
            if impacts:
                impact_df = pd.DataFrame(impacts, columns=["Factor", "Impact (Points)", "Priority", "Suggestion"])
                st.dataframe(impact_df, use_container_width=True, hide_index=True)
            else:
                st.success("✅ All factors are optimal! Great job!")
        
        with tab3:
            st.markdown("### 📈 Detailed Comparison Chart")
            
            if hours > 0 or attendance > 0 or sleep > 0 or previous > 0:
                categories_radar = ['Study Hours', 'Attendance', 'Sleep', 'Previous Score', 'Motivation', 'Teacher Quality']
                values_radar = [
                    min(100, (hours / 8) * 100) if hours > 0 else 0,
                    attendance if attendance > 0 else 0,
                    min(100, (sleep / 9) * 100) if sleep > 0 else 0,
                    previous if previous > 0 else 0,
                    100 if motivation == "High" else (50 if motivation == "Medium" else 25),
                    100 if teacher == "Good" else (50 if teacher == "Average" else 25)
                ]
                
                fig_radar = go.Figure(data=go.Scatterpolar(
                    r=values_radar,
                    theta=categories_radar,
                    fill='toself',
                    marker_color='#00ff88' if st.session_state.dark_mode else '#667eea'
                ))
                
                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=False,
                    height=450,
                    template='plotly_dark' if st.session_state.dark_mode else 'plotly_white',
                    title="Performance Radar Chart"
                )
                
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Enter values above to see radar chart")
        
        with tab4:
            user_pred_df = get_user_predictions(st.session_state.user['id'])
            if len(user_pred_df) > 1:
                st.markdown("### 📈 Your Score Trend Over Time")
                fig = px.line(user_pred_df.head(10), x='prediction_date', y='predicted_score',
                             title="Score Progress Tracking", markers=True)
                fig.update_layout(height=400, 
                                template='plotly_dark' if st.session_state.dark_mode else 'plotly_white')
                st.plotly_chart(fig, use_container_width=True)
                
                if len(user_pred_df) >= 2:
                    first = user_pred_df.iloc[-1]['predicted_score']
                    last = user_pred_df.iloc[0]['predicted_score']
                    improvement = last - first
                    color = "#00ff88" if improvement > 0 else "#ff6b6b"
                    st.markdown(f"""
                        <div style="text-align: center; padding: 1rem;">
                            <h3 style="color: {color};">📈 Your score has {'increased' if improvement > 0 else 'decreased'} by {abs(improvement)} points since your first prediction!</h3>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("📊 Make more predictions to see your progress over time!")
        
        # Download Report Button - Fixed
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
        with col_btn2:
            if st.button("📥 Download Detailed Report (PDF)", use_container_width=True):
                with st.spinner("Generating your report..."):
                    try:
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
                        st.success("✅ Report generated successfully!")
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
                        st.info("Please try again or contact support.")

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <p>🎓 Student Score Predictor | Based on Machine Learning Analysis</p>
        <p style="font-size: 0.8rem;">This tool provides predictions based on historical data patterns.</p>
    </div>
""", unsafe_allow_html=True)
