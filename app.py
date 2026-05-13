import streamlit as st
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Import custom modules
from database import init_database, save_prediction, get_user_predictions
from auth import init_session_state, login_page, register_page, admin_panel
from report_generator import generate_pdf_report

# Initialize database and session
init_database()
init_session_state()

# Page configuration
st.set_page_config(
    page_title="Student Score Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
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
    .score-display {
        font-size: 4rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    .sidebar-content {
        padding: 1rem;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-weight: bold;
        border-radius: 10px;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .info-box {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    </style>
""", unsafe_allow_html=True)

# Load model
@st.cache_resource
def load_model():
    try:
        model = joblib.load("student_model.pkl")
        columns = joblib.load("model_columns.pkl")
        return model, columns
    except FileNotFoundError:
        st.error("❌ Model files not found! Please ensure 'student_model.pkl' and 'model_columns.pkl' are in the same directory.")
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
    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    st.stop()

# Load model for students
model, model_columns = load_model()

# Sidebar - User Profile
with st.sidebar:
    st.markdown("## 👤 Student Profile")
    st.markdown(f"**Name:** {st.session_state.user['full_name']}")
    st.markdown(f"**🏫 School:** {st.session_state.user['school_name']}")
    if st.session_state.user.get('grade'):
        st.markdown(f"**📚 Grade:** {st.session_state.user['grade']}")
    if st.session_state.user.get('email'):
        st.markdown(f"**📧 Email:** {st.session_state.user['email']}")
    
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
        
        # Recent trend
        if len(user_pred_df) >= 2:
            latest = user_pred_df.iloc[0]['predicted_score']
            previous = user_pred_df.iloc[1]['predicted_score']
            change = latest - previous
            st.metric("Recent Trend", f"{change:+.0f} points", 
                     delta_color="normal" if change >= 0 else "inverse")
    
    st.markdown("---")
    
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
    
    st.markdown("---")
    st.caption(f"© 2024 Student Score Predictor\nLogged in as: {st.session_state.user['username']}")

# Main content
st.markdown(f"""
    <div class="main-header">
        <h1>🎓 Welcome, {st.session_state.user['full_name']}!</h1>
        <p>Predict your exam score and get personalized recommendations to improve</p>
    </div>
""", unsafe_allow_html=True)

# Input Form
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="input-section">', unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: center; color: #667eea;'>📝 Student Information</h2>", unsafe_allow_html=True)
    
    with st.form("prediction_form"):
        # Academic Information
        st.markdown("### 📚 Academic Information")
        col_a, col_b = st.columns(2)
        with col_a:
            hours = st.slider("Hours Studied per Day", 0.0, 24.0, 0.0, 0.5, 
                            help="Recommended: 6-8 hours for optimal performance")
            attendance = st.slider("Attendance Percentage", 0.0, 100.0, 0.0, 5.0,
                                  help="Below 85% significantly impacts performance")
            previous = st.slider("Previous Exam Score", 0.0, 100.0, 0.0, 5.0)
        with col_b:
            tutoring = st.slider("Tutoring Sessions per Week", 0, 10, 0, 1)
            sleep = st.slider("Sleep Hours per Night", 0.0, 12.0, 0.0, 0.5)
            distance = st.slider("Distance from Home (km)", 0.0, 50.0, 0.0, 1.0)
        
        # Personal Factors
        st.markdown("### 💪 Personal Factors")
        col_c, col_d = st.columns(2)
        with col_c:
            physical_activity = st.slider("Physical Activity (hours/week)", 0, 20, 0, 1)
            health = st.slider("Health Status (1=Poor, 5=Excellent)", 1, 5, 1)
        with col_d:
            motivation = st.selectbox("Motivation Level", ["Low", "Medium", "High"], index=0)
            teacher = st.selectbox("Teacher Quality", ["Poor", "Average", "Good"], index=0)
        
        # School & Environment
        st.markdown("### 🏫 School & Environment")
        col_e, col_f = st.columns(2)
        with col_e:
            school = st.selectbox("School Type", ["Public", "Private"], index=0)
            internet = st.selectbox("Internet Access", ["No", "Yes"], index=0)
            income = st.selectbox("Family Income", ["Low", "Medium", "High"], index=0)
        with col_f:
            parent = st.selectbox("Parental Involvement", ["Low", "Medium", "High"], index=0)
            parent_education = st.selectbox("Parent Education", ["School", "College", "Postgraduate"], index=0)
            peer = st.selectbox("Peer Influence", ["Negative", "Neutral", "Positive"], index=0)
        
        # Resources & Activities
        st.markdown("### 🎯 Resources & Activities")
        col_g, col_h = st.columns(2)
        with col_g:
            resources = st.selectbox("Learning Resources Access", ["Low", "Medium", "High"], index=0)
            activities = st.selectbox("Extracurricular Activities", ["No", "Yes"], index=0)
        with col_h:
            study_env = st.selectbox("Study Environment", ["Poor", "Average", "Good"], index=0)
        
        st.markdown("---")
        submitted = st.form_submit_button("🎯 Predict My Score", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Handle prediction
if 'submitted' in locals() and submitted:
    with st.spinner("Analyzing your data and generating prediction..."):
        # Prepare input data
        input_data = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring,
            "Sleep_Hours": sleep,
            "Distance_from_Home": distance,
            "Physical_Activity": physical_activity,
            "Health": health,
            "Motivation_Level": motivation,
            "Teacher_Quality": teacher,
            "School_Type": school,
            "Internet_Access": internet,
            "Family_Income": income,
            "Parental_Involvement": parent,
            "Parental_Education_Level": parent_education,
            "Peer_Influence": peer,
            "Learning_Resources": resources,
            "Extracurricular_Activities": activities,
            "Study_Environment": study_env,
        }
        
        # Prepare for model
        data_for_model = {
            "Hours_Studied": hours,
            "Attendance": attendance,
            "Previous_Scores": previous,
            "Tutoring_Sessions": tutoring,
            "Sleep_Hours": sleep,
            "Distance_from_Home": distance,
            "Physical_Activity": physical_activity,
            "Health": health,
            "Motivation_Level_Low": 1 if motivation == "Low" else 0,
            "Motivation_Level_Medium": 1 if motivation == "Medium" else 0,
            "Teacher_Quality_Good": 1 if teacher == "Good" else 0,
            "Teacher_Quality_Poor": 1 if teacher == "Poor" else 0,
            "School_Type_Public": 1 if school == "Public" else 0,
            "Internet_Access_Yes": 1 if internet == "Yes" else 0,
            "Family_Income_Low": 1 if income == "Low" else 0,
            "Family_Income_Medium": 1 if income == "Medium" else 0,
            "Parental_Involvement_Low": 1 if parent == "Low" else 0,
            "Parental_Involvement_Medium": 1 if parent == "Medium" else 0,
            "Parental_Education_Level_Postgraduate": 1 if parent_education == "Postgraduate" else 0,
            "Parental_Education_Level_School": 1 if parent_education == "School" else 0,
            "Peer_Influence_Neutral": 1 if peer == "Neutral" else 0,
            "Peer_Influence_Positive": 1 if peer == "Positive" else 0,
            "Access_to_Resources_Low": 1 if resources == "Low" else 0,
            "Access_to_Resources_Medium": 1 if resources == "Medium" else 0,
            "Extracurricular_Activities_Yes": 1 if activities == "Yes" else 0,
            "Study_Environment_Good": 1 if study_env == "Good" else 0,
            "Study_Environment_Poor": 1 if study_env == "Poor" else 0,
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
        if hours < 5:
            recommendations.append("📖 Increase study hours to 6-8 per day for better results")
        elif hours > 12:
            recommendations.append("😴 Reduce study hours to avoid burnout - quality over quantity")
        if sleep < 6:
            recommendations.append("😴 Get more sleep (7-9 hours) to improve memory and focus")
        if attendance < 85:
            recommendations.append("🏫 Improve attendance - regular classes increase understanding by up to 30%")
        if motivation == "Low":
            recommendations.append("🎯 Set small daily goals and reward yourself to boost motivation")
        if teacher == "Poor" and resources == "Low":
            recommendations.append("📚 Seek online resources like Khan Academy, YouTube tutorials")
        if parent == "Low":
            recommendations.append("👨‍👩‍👧 Discuss your studies with parents - their support helps!")
        if peer == "Negative":
            recommendations.append("👥 Join positive study groups with motivated students")
        if physical_activity < 2:
            recommendations.append("🏃 Exercise 2-3 hours weekly - it improves brain function")
        if health < 3:
            recommendations.append("💪 Focus on health - eat well and take breaks")
        
        if not recommendations:
            recommendations = ["🌟 Great habits! Keep maintaining your current routine"]
        
        # Save to database
        save_prediction(st.session_state.user['id'], st.session_state.user['username'], 
                       input_data, final_score, " | ".join(recommendations[:5]))
        
        # Display prediction
        st.markdown("---")
        st.markdown(f"""
            <div class="prediction-card">
                <h2>🎯 Your Predicted Exam Score</h2>
                <div class="score-display">{final_score}/100</div>
                <p>Based on your inputs and historical data patterns</p>
            </div>
        """, unsafe_allow_html=True)
        
        # Grade and message
        if final_score >= 90:
            grade, color, emoji = "A+", "#4CAF50", "🌟"
            message = "Outstanding performance! You're in the top tier!"
        elif final_score >= 80:
            grade, color, emoji = "A", "#8BC34A", "🎉"
            message = "Very good! Keep up the momentum!"
        elif final_score >= 70:
            grade, color, emoji = "B", "#FFC107", "📈"
            message = "Good performance. Consistent effort will lead to improvement."
        elif final_score >= 60:
            grade, color, emoji = "C", "#FF9800", "📚"
            message = "Satisfactory. More focused study time recommended."
        elif final_score >= 50:
            grade, color, emoji = "D", "#FF5722", "⚠️"
            message = "Needs improvement. Consider tutoring or study groups."
        else:
            grade, color, emoji = "F", "#f44336", "🔴"
            message = "Critical level. Immediate intervention recommended."
        
        col_g1, col_g2, col_g3 = st.columns([1, 2, 1])
        with col_g2:
            st.markdown(f"""
                <div class="info-box">
                    <h3 style="color: {color}; text-align: center;">{emoji} Grade: {grade}</h3>
                    <p style="text-align: center;">{message}</p>
                </div>
            """, unsafe_allow_html=True)
        
        # Tabs for detailed analysis
        tab1, tab2, tab3 = st.tabs(["📊 Performance Analysis", "💡 Recommendations", "📈 Historical Trend"])
        
        with tab1:
            # Create comparison chart
            fig = go.Figure()
            
            categories = ['Study Hours', 'Attendance', 'Sleep', 'Previous Score', 'Predicted Score']
            values = [hours, attendance, sleep, previous, final_score]
            optimal = [7, 85, 8, 85, 85]
            
            fig.add_trace(go.Bar(name='Your Value', x=categories, y=values, marker_color='#667eea'))
            fig.add_trace(go.Bar(name='Optimal Range', x=categories, y=optimal, marker_color='#ff6b6b', opacity=0.7))
            
            fig.update_layout(
                title="Your Performance vs Optimal Ranges",
                xaxis_title="Metrics",
                yaxis_title="Value",
                barmode='group',
                height=450,
                template='plotly_white'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Key metrics
            st.markdown("### Key Metrics Analysis")
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                study_gap = hours - 7
                st.metric("Study Hours", f"{hours} hrs", f"{study_gap:+.1f} from optimal")
            with col_m2:
                attend_gap = attendance - 85
                st.metric("Attendance", f"{attendance}%", f"{attend_gap:+.0f}%")
            with col_m3:
                sleep_gap = sleep - 8
                st.metric("Sleep Hours", f"{sleep} hrs", f"{sleep_gap:+.1f} hrs")
            with col_m4:
                score_gap = final_score - 85
                st.metric("Target vs Actual", f"{final_score}", f"{score_gap:+.0f}")
        
        with tab2:
            st.markdown("### 💡 Personalized Recommendations")
            for i, rec in enumerate(recommendations, 1):
                st.markdown(f"{i}. {rec}")
            
            # Impact analysis
            st.markdown("### 📊 Priority Improvement Areas")
            impacts = []
            if hours < 6:
                impacts.append(("Low Study Hours", -15, "HIGH", "Increase to 6-8 hours"))
            if hours > 10:
                impacts.append(("Excessive Study", -5, "MEDIUM", "Take more breaks"))
            if attendance < 85:
                impacts.append(("Low Attendance", -12, "HIGH", "Improve attendance"))
            if sleep < 7:
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
            # History comparison
            user_pred_df = get_user_predictions(st.session_state.user['id'])
            if len(user_pred_df) > 1:
                st.markdown("### 📈 Your Score Trend Over Time")
                fig = px.line(user_pred_df.head(10), x='prediction_date', y='predicted_score',
                             title="Score Progress Tracking", markers=True)
                fig.update_layout(height=400, template='plotly_white')
                st.plotly_chart(fig, use_container_width=True)
                
                # Improvement rate
                if len(user_pred_df) >= 2:
                    first = user_pred_df.iloc[-1]['predicted_score']
                    last = user_pred_df.iloc[0]['predicted_score']
                    improvement = last - first
                    st.info(f"📈 Your score has {'increased' if improvement > 0 else 'decreased'} by {abs(improvement)} points since your first prediction!")
            else:
                st.info("📊 Make more predictions to see your progress over time!")
        
        # Download Report Button
        st.markdown("---")
        if st.button("📥 Download Detailed Report (PDF)", use_container_width=True):
            with st.spinner("Generating your comprehensive report..."):
                # Create comparison chart for PDF
                fig_pdf, ax = plt.subplots(figsize=(10, 5))
                categories_pdf = ['Study Hours', 'Attendance', 'Sleep', 'Previous Score']
                values_pdf = [hours, attendance, sleep, previous]
                optimal_pdf = [7, 85, 8, 85]
                
                x = range(len(categories_pdf))
                width = 0.35
                ax.bar([i - width/2 for i in x], values_pdf, width, label='Your Value', color='#667eea')
                ax.bar([i + width/2 for i in x], optimal_pdf, width, label='Optimal Range', color='#ff6b6b', alpha=0.7)
                ax.set_xlabel('Metrics')
                ax.set_ylabel('Value')
                ax.set_title('Performance Comparison')
                ax.set_xticks(x)
                ax.set_xticklabels(categories_pdf)
                ax.legend()
                ax.grid(True, alpha=0.3)
                
                # Save chart
                chart_path = "temp_chart.png"
                plt.savefig(chart_path, bbox_inches='tight', dpi=100)
                plt.close()
                
                # Generate PDF
                pdf_buffer = generate_pdf_report(
                    st.session_state.user,
                    input_data,
                    final_score,
                    recommendations,
                    chart_path
                )
                
                # Download button
                st.download_button(
                    label="💾 Download PDF Report",
                    data=pdf_buffer,
                    file_name=f"student_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; padding: 1rem; color: #666;">
        <p>🎓 Student Score Predictor | Based on Machine Learning Analysis</p>
        <p style="font-size: 0.8rem;">This tool provides predictions based on historical data patterns. Actual results may vary.</p>
    </div>
""", unsafe_allow_html=True)
