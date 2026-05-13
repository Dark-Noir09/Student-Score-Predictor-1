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
            max-width: 400px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        st.markdown('<div class="login-header"><h1>🎓 Student Score Predictor</h1><p>Login to access your dashboard</p></div>', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username")
        password = st.text_input("Password", type="password", key="login_password")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Login", use_container_width=True):
                user = login_user(username, password)
                if user:
                    st.session_state.logged_in = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid username or password")
        
        with col2:
            if st.button("Create Account", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def register_page():
    """Render registration page"""
    st.markdown("""
        <style>
        .register-container {
            max-width: 500px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.container():
        st.markdown('<div class="register-container">', unsafe_allow_html=True)
        
        st.markdown("<h1 style='text-align: center;'>📝 Create Account</h1>", unsafe_allow_html=True)
        
        with st.form("register_form"):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username")
            email = st.text_input("Email")
            school_name = st.text_input("School/College Name")
            grade = st.text_input("Grade/Year")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("Register", use_container_width=True)
            with col2:
                if st.form_submit_button("Back to Login", use_container_width=True):
                    st.session_state.page = 'login'
                    st.rerun()
            
            if submitted:
                if password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    success, message = register_user(username, password, full_name, school_name, grade, email)
                    if success:
                        st.success(message)
                        st.info("Please login with your credentials")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(message)
        
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
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="admin-header"><h1>🔐 Admin Panel</h1><p>Manage users and view predictions</p></div>', unsafe_allow_html=True)
    
    from database import get_all_predictions
    
    predictions_df = get_all_predictions()
    
    if not predictions_df.empty:
        st.subheader("📊 All User Predictions")
        
        # Stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Predictions", len(predictions_df))
        with col2:
            st.metric("Unique Users", predictions_df['username'].nunique())
        with col3:
            st.metric("Average Score", round(predictions_df['predicted_score'].mean(), 1))
        with col4:
            st.metric("High Scorers (90+)", len(predictions_df[predictions_df['predicted_score'] >= 90]))
        
        # Search filter
        search = st.text_input("🔍 Search by username or name")
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
                "predicted_score": st.column_config.NumberColumn("Score", format="%d"),
                "prediction_date": st.column_config.DatetimeColumn("Date"),
            }
        )
        
        # Export option
        csv = predictions_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name="predictions_export.csv",
            mime="text/csv"
        )
    else:
        st.info("No predictions yet")
