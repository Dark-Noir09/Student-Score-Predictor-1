import streamlit as st
from database import login_user, register_user

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'

def login_page():
    """Render login page"""
    st.markdown("""
        <style>
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-top: 50px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            color: #667eea;
            margin-bottom: 0.5rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-header"><h1>🎓 Student Score Predictor</h1><p>Login to access your dashboard</p></div>', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True, type="primary"):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user = user
                        st.rerun()
                    else:
                        st.error("Invalid username or password")
                else:
                    st.warning("Please enter username and password")
        
        with col2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        st.markdown("---")
        st.caption("Demo Admin Access: username: admin, password: admin123")
        st.markdown('</div>', unsafe_allow_html=True)

def register_page():
    """Render registration page"""
    st.markdown("""
        <style>
        .register-container {
            max-width: 550px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-top: 50px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="register-container">', unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center; color: #667eea;'>📝 Create Account</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Join us to track your academic progress</p>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            col1, col2 = st.columns(2)
            with col1:
                full_name = st.text_input("Full Name *", placeholder="John Doe")
                username = st.text_input("Username *", placeholder="johndoe")
                email = st.text_input("Email", placeholder="john@example.com")
            with col2:
                school_name = st.text_input("School/College Name *", placeholder="Your School Name")
                grade = st.text_input("Grade/Year", placeholder="12th Grade")
                password = st.text_input("Password *", type="password", placeholder="Min 4 characters")
                confirm_password = st.text_input("Confirm Password *", type="password")
            
            submitted = st.form_submit_button("Register", use_container_width=True, type="primary")
            
            if submitted:
                if not full_name or not username or not password or not school_name:
                    st.error("Please fill in all required fields (*)")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    success, message = register_user(username, password, full_name, school_name, grade, email)
                    if success:
                        st.success(message)
                        st.balloons()
                        st.info("Please login with your credentials")
                        import time
                        time.sleep(2)
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(message)
            
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.page = 'login'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def admin_panel():
    """Render admin panel"""
    st.markdown("""
        <style>
        .admin-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 10px;
            color: white;
            margin-bottom: 2rem;
        }
        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="admin-header"><h1>🔐 Admin Panel</h1><p>Manage users and view all predictions</p></div>', unsafe_allow_html=True)
    
    from database import get_all_predictions
    
    predictions_df = get_all_predictions()
    
    if not predictions_df.empty:
        st.subheader("📊 Dashboard Overview")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Total Predictions", len(predictions_df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Unique Users", predictions_df['username'].nunique())
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            st.metric("Average Score", f"{predictions_df['predicted_score'].mean():.1f}")
            st.markdown('</div>', unsafe_allow_html=True)
        with col4:
            st.markdown('<div class="stat-card">', unsafe_allow_html=True)
            high_scores = len(predictions_df[predictions_df['predicted_score'] >= 90])
            st.metric("High Scorers (90+)", high_scores)
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        st.subheader("📋 All Predictions")
        
        # Search filter
        search = st.text_input("🔍 Search by username or name", placeholder="Type to search...")
        if search:
            predictions_df = predictions_df[
                predictions_df['username'].str.contains(search, case=False) |
                predictions_df['full_name'].str.contains(search, case=False)
            ]
        
        # Display table
        st.dataframe(
            predictions_df,
            use_container_width=True,
            column_config={
                "id": "ID",
                "username": "Username",
                "full_name": "Full Name",
                "school_name": "School",
                "grade": "Grade",
                "email": "Email",
                "predicted_score": st.column_config.NumberColumn("Score", format="%d"),
                "prediction_date": st.column_config.DatetimeColumn("Date"),
            },
            hide_index=True
        )
        
        # Export option
        csv = predictions_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"predictions_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📭 No predictions yet. Users will appear here once they make predictions.")
