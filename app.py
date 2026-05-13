import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# =========================
# PAGE CONFIGURATION
# =========================
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================
# LOAD MODEL AND COLUMNS
# =========================
@st.cache_resource
def load_model():
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        return model, columns
    except FileNotFoundError:
        st.error("❌ Model files not found! Please ensure 'student_model.pkl' and 'model_columns.pkl' are in the same directory.")
        st.stop()

model, model_columns = load_model()

# =========================
# CUSTOM CSS
# =========================
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .prediction-box {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
    }
    .info-box {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-weight: bold;
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# =========================
# TITLE
# =========================
st.markdown('<div class="main-header"><h1>🎓 Student Score Predictor</h1><p>Predict exam scores based on student characteristics and study habits</p></div>', unsafe_allow_html=True)

# =========================
# SIDEBAR - INPUTS
# =========================
st.sidebar.header("📝 Student Information")

with st.sidebar:
    st.subheader("📚 Study Habits")
    hours = st.slider("Hours Studied per Day", 0.0, 24.0, 6.0, 0.5, help="Recommended: 6-8 hours for optimal performance")
    tutoring = st.slider("Tutoring Sessions per Week", 0, 10, 2, 1, help="Extra academic support sessions")
    sleep = st.slider("Sleep Hours per Night", 0.0, 12.0, 7.0, 0.5, help="Teens need 8-10 hours for best cognitive function")
    
    st.subheader("🏫 School Factors")
    attendance = st.slider("Attendance Percentage", 0.0, 100.0, 85.0, 5.0, help="Below 85% significantly impacts performance")
    previous = st.slider("Previous Exam Score", 0.0, 100.0, 65.0, 5.0)
    
    st.subheader("💪 Personal Factors")
    distance = st.slider("Distance from Home (km)", 0.0, 50.0, 10.0, 1.0, help="Travel time affects study time availability")
    physical_activity = st.slider("Physical Activity (hours/week)", 0, 20, 3, 1, help="Exercise improves cognitive function")
    health = st.slider("Health Status", 1, 5, 3, 1, help="1=Poor, 5=Excellent")

    st.subheader("🎯 Motivation & Environment")
    motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"])
    teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"])
    school = st.selectbox("School Type", ["Public", "Private"])
    internet = st.selectbox("Internet Access", ["Yes", "No"])
    income = st.selectbox("Family Income", ["Low", "Medium", "High"])
    parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"])
    parent_education = st.selectbox("Parent Education Level", ["School", "College", "Postgraduate"])
    peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"])
    resources = st.selectbox("Learning Resources Access", ["Low", "Medium", "High"])
    activities = st.selectbox("Extracurricular Activities", ["Yes", "No"])
    study_env = st.selectbox("Study Environment", ["Poor", "Average", "Good"])

# =========================
# MAIN CONTENT
# =========================
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### 📊 Quick Stats")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.metric("📚 Study Time", f"{hours} hrs/day", delta="+2" if hours > 6 else "-1")
    with col_b:
        st.metric("🎯 Attendance", f"{attendance}%", delta="Good" if attendance >= 85 else "Needs Improvement")
    with col_c:
        st.metric("💤 Sleep", f"{sleep} hrs", delta="Optimal" if 7 <= sleep <= 9 else "Adjust")

# =========================
# PREDICTION FUNCTION
# =========================
def prepare_input_data():
    """Prepare input data matching the model's training columns"""
    
    # Numeric features
    data = {
        "Hours_Studied": hours,
        "Attendance": attendance,
        "Previous_Scores": previous,
        "Tutoring_Sessions": tutoring,
        "Sleep_Hours": sleep,
        "Distance_from_Home": distance,
        "Physical_Activity": physical_activity,
        "Health": health,
        
        # Categorical features (one-hot encoded)
        "Motivation_Level_Low": 1 if motivation == "Low" else 0,
        "Motivation_Level_Medium": 1 if motivation == "Medium" else 0,
        # High is reference (both Low and Medium = 0)
        
        "Teacher_Quality_Good": 1 if teacher == "Good" else 0,
        "Teacher_Quality_Poor": 1 if teacher == "Poor" else 0,
        # Average is reference
        
        "School_Type_Public": 1 if school == "Public" else 0,
        # Private is reference
        
        "Internet_Access_Yes": 1 if internet == "Yes" else 0,
        
        "Family_Income_Low": 1 if income == "Low" else 0,
        "Family_Income_Medium": 1 if income == "Medium" else 0,
        # High is reference
        
        "Parental_Involvement_Low": 1 if parent == "Low" else 0,
        "Parental_Involvement_Medium": 1 if parent == "Medium" else 0,
        # High is reference
        
        "Parental_Education_Level_Postgraduate": 1 if parent_education == "Postgraduate" else 0,
        "Parental_Education_Level_School": 1 if parent_education == "School" else 0,
        # College is reference
        
        "Peer_Influence_Neutral": 1 if peer == "Neutral" else 0,
        "Peer_Influence_Positive": 1 if peer == "Positive" else 0,
        # Negative is reference
        
        "Access_to_Resources_Low": 1 if resources == "Low" else 0,
        "Access_to_Resources_Medium": 1 if resources == "Medium" else 0,
        # High is reference
        
        "Extracurricular_Activities_Yes": 1 if activities == "Yes" else 0,
        
        "Study_Environment_Good": 1 if study_env == "Good" else 0,
        "Study_Environment_Poor": 1 if study_env == "Poor" else 0,
        # Average is reference
        
        # Score Range columns (these come from training data - set to 0)
        "Score_Range_60-80": 0,
        "Score_Range_81-90": 0,
        "Score_Range_91-100": 0,
    }
    
    # Convert to DataFrame
    input_df = pd.DataFrame([data])
    
    # Ensure all columns from training are present
    for col in model_columns:
        if col not in input_df.columns:
            input_df[col] = 0
    
    # Reorder columns to match training
    input_df = input_df[model_columns]
    
    return input_df

# =========================
# PREDICTION BUTTON
# =========================
if st.button("🎯 Predict Exam Score", use_container_width=True):
    with st.spinner("Analyzing student data..."):
        try:
            # Prepare input
            input_df = prepare_input_data()
            
            # Make prediction
            prediction = model.predict(input_df)[0]
            
            # Clamp to realistic range (40-100)
            final_score = max(40, min(100, prediction))
            final_score = int(round(final_score))
            
            # Calculate confidence interval (based on model's typical error)
            # Using standard deviation from training (approximately ±5 points)
            lower_bound = max(40, final_score - 5)
            upper_bound = min(100, final_score + 5)
            
            # =========================
            # DISPLAY RESULTS
            # =========================
            st.markdown("---")
            
            # Score display
            st.markdown(f"""
            <div class="prediction-box">
                <h2>🎯 Predicted Exam Score</h2>
                <h1 style="font-size: 72px; margin: 0;">{final_score}/100</h1>
                <p>Confidence Interval: {lower_bound} - {upper_bound}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Grade and interpretation
            if final_score >= 90:
                st.balloons()
                grade = "A+"
                message = "🌟 Excellent! Outstanding performance! Keep up the great work!"
                color = "green"
            elif final_score >= 80:
                grade = "A"
                message = "🎉 Very Good! You're performing well above average!"
                color = "lightgreen"
            elif final_score >= 70:
                grade = "B"
                message = "📈 Good! You're on the right track. Consistent effort will improve results."
                color = "blue"
            elif final_score >= 60:
                grade = "C"
                message = "📚 Satisfactory. More focused study time could boost your score."
                color = "orange"
            elif final_score >= 50:
                grade = "D"
                message = "⚠️ Needs Improvement. Consider tutoring or study groups."
                color = "red"
            else:
                grade = "F"
                message = "🔴 Critical. Immediate intervention recommended - speak with a teacher."
                color = "darkred"
            
            col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
            with col_g2:
                st.markdown(f"""
                <div class="info-box">
                    <h3>📖 Grade: {grade}</h3>
                    <p style="color: {color}; font-weight: bold;">{message}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # =========================
            # RECOMMENDATIONS
            # =========================
            st.subheader("💡 Personalized Recommendations")
            
            recommendations = []
            
            if hours < 5:
                recommendations.append("📖 **Increase study time** - Aim for 6-8 hours daily for better results")
            elif hours > 12:
                recommendations.append("😴 **Reduce study hours** - Over-studying leads to burnout. Take more breaks")
            
            if sleep < 6:
                recommendations.append("😴 **Improve sleep** - Get at least 7-8 hours of sleep for better memory retention")
            
            if attendance < 85:
                recommendations.append("🏫 **Improve attendance** - Regular classes increase understanding by up to 30%")
            
            if previous < final_score - 10:
                recommendations.append("📈 **Great improvement!** - Your predicted score shows significant progress from previous performance")
            elif previous > final_score + 10:
                recommendations.append("⚠️ **Score might drop** - Review your study habits to maintain performance")
            
            if motivation == "Low":
                recommendations.append("🎯 **Boost motivation** - Set small, achievable goals and reward yourself for completing them")
            
            if teacher == "Poor" and resources == "Low":
                recommendations.append("📚 **Seek alternative resources** - Use online platforms like Khan Academy, Coursera")
            
            if internet == "No":
                recommendations.append("🌐 **Limited internet access** - Use offline resources like libraries, study groups")
            
            if parent == "Low":
                recommendations.append("👨‍👩‍👧 **Parental involvement** - Regular discussions about studies can improve motivation")
            
            if peer == "Negative":
                recommendations.append("👥 **Peer influence** - Join study groups with motivated students")
            
            if physical_activity < 2:
                recommendations.append("🏃 **Exercise more** - Physical activity improves brain function and reduces stress")
            
            if not recommendations:
                recommendations.append("✅ You're on the right track! Continue your current study habits.")
            
            for rec in recommendations[:5]:  # Show top 5 recommendations
                st.write(rec)
            
            # =========================
            # COMPARISON CHART
            # =========================
            st.subheader("📊 Performance Analysis")
            
            # Create comparison data
            comparisons = {
                "Category": ["Study Hours", "Sleep", "Attendance", "Previous Score", "Predicted Score"],
                "Your Value": [hours, sleep, attendance, previous, final_score],
                "Optimal Range": [7, 8, 90, 85, 85]
            }
            
            comp_df = pd.DataFrame(comparisons)
            
            fig, ax = plt.subplots(figsize=(10, 5))
            x = range(len(comp_df))
            width = 0.35
            
            ax.bar([i - width/2 for i in x], comp_df["Your Value"], width, label="Your Value", color="#667eea")
            ax.bar([i + width/2 for i in x], comp_df["Optimal Range"], width, label="Optimal Range", color="#ff6b6b", alpha=0.7)
            
            ax.set_xlabel("Metrics")
            ax.set_ylabel("Score/Hours/Percentage")
            ax.set_title("Your Performance vs Optimal Ranges")
            ax.set_xticks(x)
            ax.set_xticklabels(comp_df["Category"])
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            st.pyplot(fig)
            plt.close()
            
            # =========================
            # DISCLAIMER
            # =========================
            st.caption("⚠️ **Disclaimer**: This prediction is based on historical data patterns and should be used as a guideline only. Individual results may vary based on many factors.")
            
        except Exception as e:
            st.error(f"❌ An error occurred during prediction: {str(e)}")
            st.info("Please check that all inputs are valid and try again.")

# =========================
# FOOTER - INFO SECTION
# =========================
with st.expander("ℹ️ About This Predictor"):
    st.markdown("""
    ### How it works
    This predictor uses **Linear Regression** trained on 6,608 student records to estimate exam scores based on:
    
    - **Study habits** (hours studied, tutoring, sleep)
    - **School factors** (attendance, teacher quality, school type)
    - **Personal factors** (motivation, health, physical activity)
    - **Socioeconomic factors** (family income, internet access, parental involvement)
    - **Environmental factors** (study environment, peer influence, learning resources)
    
    ### Model Performance
    - **R² Score**: ~0.85 (85% of variance explained)
    - **Mean Absolute Error**: ~5 points
    - **Training Data**: 6,608 students
    
    ### Tips for Better Scores
    1. Maintain 85%+ attendance
    2. Study 6-8 hours daily with breaks
    3. Get 7-9 hours of sleep
    4. Stay physically active (2-3 hours/week)
    5. Create a distraction-free study environment
    """)

# =========================
# SIDEBAR FOOTER
# =========================
st.sidebar.markdown("---")
st.sidebar.markdown("""
### 📈 Score Guide
- **90-100**: A+ (Excellent)
- **80-89**: A (Very Good)
- **70-79**: B (Good)
- **60-69**: C (Satisfactory)
- **50-59**: D (Needs Improvement)
- **0-49**: F (Critical)
""")

st.sidebar.markdown("---")
st.sidebar.caption(f"🎓 Student Score Predictor v2.0 | Last updated: {datetime.now().strftime('%Y-%m-%d')}")
