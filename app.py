import streamlit as st
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

from database import init_database, save_prediction, get_user_predictions
from auth import init_session_state, login_page, register_page, admin_panel
from report_generator import generate_pdf_report

init_database()
init_session_state()

st.set_page_config(page_title="Student Score Predictor", page_icon="🎓", layout="wide")

def toggle_dark_mode():
    st.session_state.dark_mode = not st.session_state.dark_mode

# CSS for themes (no stray divs)
if st.session_state.dark_mode:
    css = """
        <style>
        .main .block-container { padding-top: 0rem !important; }
        header, #MainMenu, footer { display: none !important; }
        .stApp { background: linear-gradient(135deg, #0a0a0a 0%, #1a1a1a 100%); }
        .main-header { background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%); padding: 1.5rem; border-radius: 20px; text-align: center; margin: 1rem 0; color: #0a0a0a; }
        .prediction-card { background: linear-gradient(135deg, #00ff88 0%, #00cc66 100%); padding: 1.5rem; border-radius: 20px; text-align: center; margin: 1rem 0; }
        .input-section { background: transparent; padding: 1.5rem; border-radius: 20px; border: 1px solid #00ff88; margin: 1rem 0; }
        .stMarkdown, label, .stSelectbox label { color: #00ff88 !important; font-size: 14px !important; }
        h1 { font-size: 28px !important; } h2 { font-size: 24px !important; } h3 { font-size: 20px !important; }
        p, li { font-size: 14px !important; }
        [data-testid="stSidebar"] { background: #0a0a0a; border-right: 1px solid #00ff88; }
        .stButton > button { background: #00ff88; color: #0a0a0a; font-weight: bold; }
        .stSlider label { font-size: 14px !important; }
        </style>
    """
else:
    css = """
        <style>
        .main .block-container { padding-top: 0rem !important; }
        header, #MainMenu, footer { display: none !important; }
        .stApp { background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); }
        .main-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 20px; text-align: center; margin: 1rem 0; color: white; }
        .prediction-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 20px; text-align: center; margin: 1rem 0; color: white; }
        .input-section { background: transparent; padding: 1.5rem; border-radius: 20px; margin: 1rem 0; }
        .stMarkdown, label, .stSelectbox label { font-size: 14px !important; }
        h1 { font-size: 28px !important; } h2 { font-size: 24px !important; } h3 { font-size: 20px !important; }
        p, li { font-size: 14px !important; }
        .stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; font-weight: bold; }
        </style>
    """
st.markdown(css, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    try:
        return joblib.load("student_model.pkl"), joblib.load("model_columns.pkl")
    except:
        st.error("Model files missing. Please ensure student_model.pkl and model_columns.pkl are present.")
        st.stop()

# Authentication
if not st.session_state.logged_in:
    if st.session_state.page == 'login':
        login_page()
    else:
        register_page()
    st.stop()

if st.session_state.user['role'] == 'admin':
    admin_panel()
    st.stop()

model, model_columns = load_model()

# Sidebar
with st.sidebar:
    # Center sidebar logo using columns
    col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
    with col_logo2:
        try:
            show_logo( width=80)
        except:
            st.markdown("<h2 style='text-align: center;'>🎓</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**Name:** {st.session_state.user['full_name']}")
    st.markdown(f"**🏫 School:** {st.session_state.user['school_name']}")
    if st.session_state.user.get('grade'):
        st.markdown(f"**📚 Grade:** {st.session_state.user['grade']}")
    st.markdown("---")
    col_d1, col_d2 = st.columns([3,1])
    with col_d1: st.markdown("**Theme Mode**")
    with col_d2:
        if st.button("🌙/☀️", key="theme_toggle"):
            toggle_dark_mode()
            st.rerun()
    st.markdown("---")
    user_pred_df = get_user_predictions(st.session_state.user['id'])
    if not user_pred_df.empty:
        st.metric("Total Predictions", len(user_pred_df))
        st.metric("Average Score", f"{user_pred_df['predicted_score'].mean():.0f}")
    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()

# Home page logo (centered)
col_logo1, col_logo2, col_logo3 = st.columns([1,2,1])
with col_logo2:
    try:
        show_logo(width=120)
    except:
        st.markdown("<h1 style='text-align: center; font-size: 4rem;'>🎓</h1>", unsafe_allow_html=True)

st.markdown(f"""
    <div class="main-header">
        <h1>Welcome, {st.session_state.user['full_name']}!</h1>
        <p>Predict your exam score and get personalized recommendations</p>
    </div>
""", unsafe_allow_html=True)

# Input form – 2 columns
st.markdown('<div class="input-section">', unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>📝 Student Information</h3>", unsafe_allow_html=True)

with st.form("prediction_form"):
    # Academic
    st.markdown("#### 📚 Academic")
    col_a, col_b = st.columns(2)
    with col_a:
        hours = st.slider("📖 Hours Studied per Day", 0.0, 24.0, 0.0, 0.5)
        previous = st.slider("📊 Previous Exam Score", 0.0, 100.0, 0.0, 5.0)
    with col_b:
        attendance = st.slider("📅 Attendance (%)", 0.0, 100.0, 0.0, 5.0)
        sleep = st.slider("😴 Sleep Hours", 0.0, 12.0, 0.0, 0.5)

    # Personal
    st.markdown("#### 💪 Personal")
    col_c, col_d = st.columns(2)
    with col_c:
        motivation = st.selectbox("🎯 Motivation", ["Low","Medium","High"], index=0)
        teacher = st.selectbox("👨‍🏫 Teacher Quality", ["Poor","Average","Good"], index=0)
        tutoring = st.selectbox("📚 Tutoring Sessions", [0,1,2,3,4], index=0)
    with col_d:
        parent = st.selectbox("👨‍👩‍👧 Parental Involvement", ["Low","Medium","High"], index=0)
        peer = st.selectbox("👥 Peer Influence", ["Negative","Neutral","Positive"], index=0)

    # Environment
    st.markdown("#### 🏫 Environment")
    col_e, col_f = st.columns(2)
    with col_e:
        school = st.selectbox("🏛️ School Type", ["Public","Private"], index=0)
        internet = st.selectbox("🌐 Internet Access", ["No","Yes"], index=0)
    with col_f:
        activities = st.selectbox("⚽ Extracurricular", ["No","Yes"], index=0)

    submitted = st.form_submit_button("🎯 Predict My Score", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# Prediction handling
if submitted:
    with st.spinner("Analyzing your data..."):
        input_data = {
            "Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring, "Sleep_Hours": sleep, "Motivation_Level": motivation,
            "Teacher_Quality": teacher, "School_Type": school, "Internet_Access": internet,
            "Parental_Involvement": parent, "Peer_Influence": peer,
            "Extracurricular_Activities": activities,
        }
        data_for_model = {
            "Hours_Studied": hours, "Attendance": attendance, "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring, "Sleep_Hours": sleep,
            "Distance_from_Home": 10, "Physical_Activity": 3, "Health": 3,
            "Motivation_Level_Low": 1 if motivation=="Low" else 0,
            "Motivation_Level_Medium": 1 if motivation=="Medium" else 0,
            "Teacher_Quality_Good": 1 if teacher=="Good" else 0,
            "Teacher_Quality_Poor": 1 if teacher=="Poor" else 0,
            "School_Type_Public": 1 if school=="Public" else 0,
            "Internet_Access_Yes": 1 if internet=="Yes" else 0,
            "Family_Income_Low": 0, "Family_Income_Medium": 0,
            "Parental_Involvement_Low": 1 if parent=="Low" else 0,
            "Parental_Involvement_Medium": 1 if parent=="Medium" else 0,
            "Parental_Education_Level_Postgraduate": 0, "Parental_Education_Level_School": 0,
            "Peer_Influence_Neutral": 1 if peer=="Neutral" else 0,
            "Peer_Influence_Positive": 1 if peer=="Positive" else 0,
            "Access_to_Resources_Low": 0, "Access_to_Resources_Medium": 0,
            "Extracurricular_Activities_Yes": 1 if activities=="Yes" else 0,
            "Study_Environment_Good": 0, "Study_Environment_Poor": 0,
            "Score_Range_60-80": 0, "Score_Range_81-90": 0, "Score_Range_91-100": 0,
        }
        input_df = pd.DataFrame([data_for_model])
        for col in model_columns:
            if col not in input_df.columns:
                input_df[col] = 0
        input_df = input_df[model_columns]
        pred = model.predict(input_df)[0]
        final_score = max(40, min(100, pred))
        final_score = int(round(final_score))

        recs = []
        if 0 < hours < 6: recs.append("📖 Increase study hours to 6-8 per day")
        if hours > 10: recs.append("😴 Reduce study hours to avoid burnout")
        if 0 < sleep < 7: recs.append("😴 Get 7-9 hours of sleep for better focus")
        if 0 < attendance < 85: recs.append("🏫 Improve attendance to 85%+")
        if motivation == "Low": recs.append("🎯 Set daily goals to boost motivation")
        if teacher == "Poor": recs.append("📚 Seek additional learning resources online")
        if parent == "Low": recs.append("👨‍👩‍👧 Discuss studies with parents for support")
        if peer == "Negative": recs.append("👥 Join positive study groups")
        if tutoring == 0: recs.append("📚 Consider tutoring sessions")
        if not recs: recs = ["🌟 Great habits! Keep maintaining your routine"]

        save_prediction(st.session_state.user['id'], st.session_state.user['username'], input_data, final_score, " | ".join(recs[:5]))

        st.markdown(f"""
            <div class="prediction-card">
                <h2>🎯 Your Predicted Exam Score</h2>
                <div style="font-size:4rem; font-weight:bold;">{final_score}/100</div>
                <p>Based on your study habits and personal factors</p>
            </div>
        """, unsafe_allow_html=True)

        if final_score >= 90: grade, emoji, msg = "A+", "🌟", "Outstanding!"
        elif final_score >= 80: grade, emoji, msg = "A", "🎉", "Very good!"
        elif final_score >= 70: grade, emoji, msg = "B", "📈", "Good!"
        elif final_score >= 60: grade, emoji, msg = "C", "📚", "Satisfactory"
        elif final_score >= 50: grade, emoji, msg = "D", "⚠️", "Needs improvement"
        else: grade, emoji, msg = "F", "🔴", "Critical"
        st.info(f"{emoji} Grade: {grade} – {msg}")

        tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "💡 Recommendations", "📈 Comparison", "📉 History"])
        with tab1:
            if hours>0 or attendance>0 or sleep>0 or previous>0:
                fig = go.Figure()
                cats = ['Study Hours','Attendance','Sleep','Prev Score','Predicted']
                vals = [hours, attendance, sleep, previous, final_score]
                opt = [7,85,8,85,85]
                fig.add_trace(go.Bar(name='Your Value', x=cats, y=vals, marker_color='#00ff88' if st.session_state.dark_mode else '#667eea'))
                fig.add_trace(go.Bar(name='Optimal', x=cats, y=opt, marker_color='#ff6b6b', opacity=0.7))
                fig.update_layout(barmode='group', height=450, template='plotly_dark' if st.session_state.dark_mode else 'plotly_white')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Enter values above to see analysis")
        with tab2:
            for i, r in enumerate(recs,1): st.write(f"{i}. {r}")
            impacts = []
            if 0 < hours < 6: impacts.append(("Low Study Hours", -15, "HIGH"))
            if 0 < attendance < 85: impacts.append(("Low Attendance", -12, "HIGH"))
            if 0 < sleep < 7: impacts.append(("Insufficient Sleep", -8, "HIGH"))
            if motivation != "High": impacts.append(("Low Motivation", -10, "MEDIUM"))
            if impacts:
                st.dataframe(pd.DataFrame(impacts, columns=["Factor","Impact","Priority"]), hide_index=True)
            else:
                st.success("✅ All factors optimal!")
        with tab3:
            if hours>0 or attendance>0 or sleep>0 or previous>0:
                radar_cats = ['Study Hours','Attendance','Sleep','Prev Score','Motivation','Teacher']
                radar_vals = [
                    min(100, (hours/8)*100) if hours>0 else 0,
                    attendance if attendance>0 else 0,
                    min(100, (sleep/9)*100) if sleep>0 else 0,
                    previous if previous>0 else 0,
                    100 if motivation=="High" else (50 if motivation=="Medium" else 25),
                    100 if teacher=="Good" else (50 if teacher=="Average" else 25)
                ]
                fig_radar = go.Figure(data=go.Scatterpolar(r=radar_vals, theta=radar_cats, fill='toself', marker_color='#00ff88' if st.session_state.dark_mode else '#667eea'))
                fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, height=450)
                st.plotly_chart(fig_radar, use_container_width=True)
            else:
                st.info("Enter values to see radar chart")
        with tab4:
            hist = get_user_predictions(st.session_state.user['id'])
            if len(hist) > 1:
                fig_line = px.line(hist.head(10), x='prediction_date', y='predicted_score', title="Score Trend", markers=True)
                fig_line.update_layout(height=400)
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("Make more predictions to see your progress")

        # Download PDF button
        st.markdown("---")
        col_btn1, col_btn2, col_btn3 = st.columns([1,2,1])
        with col_btn2:
            if st.button("📥 Download Detailed Report (PDF)", use_container_width=True):
                with st.spinner("Generating PDF report..."):
                    try:
                        pdf = generate_pdf_report(st.session_state.user, input_data, final_score, recs)
                        st.download_button(
                            label="💾 Click to Save PDF Report",
                            data=pdf,
                            file_name=f"student_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        st.success("✅ Report ready! Click the button above to save.")
                    except Exception as e:
                        st.error(f"Error generating report: {str(e)}")
                        st.info("Please try again or contact support.")

st.markdown("---")
st.markdown('<div style="text-align: center;"><p>🎓 Student Score Predictor | Based on Machine Learning Analysis</p><p style="font-size: 0.8rem;">Predictions based on historical data patterns.</p></div>', unsafe_allow_html=True)
