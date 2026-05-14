import streamlit as st
from database import login_user, register_user, get_all_predictions, get_all_users, delete_user
from datetime import datetime

def init_session_state():
    """Initialize session state variables"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def login_page():
    """Render login page"""
    st.markdown("""
        <style>
        /* Completely remove ALL default Streamlit padding and margins */
        #root > div:first-child {
            padding-top: 0 !important;
        }
        .main > div {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
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
        /* Remove empty space at top of app */
        .stApp {
            margin-top: 0px !important;
            padding-top: 0px !important;
        }
        .login-container {
            max-width: 450px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-top: 0px;
        }
        .login-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .login-header h1 {
            color: #667eea;
            margin-bottom: 0.5rem;
            font-size: 1.8rem;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 1rem;
        }
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 0.75rem;
            font-weight: bold;
            border-radius: 10px;
            width: 100%;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            transition: transform 0.2s;
        }
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Create a container with no extra spacing
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # Centered Logo
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            st.image("logo.png", width=120, use_column_width=False)
        except:
            st.markdown("<h1 style='text-align: center; font-size: 3rem; margin:0;'>🎓</h1>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="login-header"><h1>Student Score Predictor</h1><p>Login to access your dashboard</p></div>', unsafe_allow_html=True)
        
        username = st.text_input("Username", key="login_username", placeholder="Enter your username", label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password", label_visibility="collapsed")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("Login", key="login_btn", use_container_width=True):
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
        
        with col_btn2:
            if st.button("Create Account", key="register_btn", use_container_width=True):
                st.session_state.page = 'register'
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def register_page():
    """Render registration page"""
    st.markdown("""
        <style>
        /* Completely remove ALL default Streamlit padding and margins */
        #root > div:first-child {
            padding-top: 0 !important;
        }
        .main > div {
            padding-top: 0 !important;
        }
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 0rem !important;
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
        }
        .register-container {
            max-width: 550px;
            margin: 0 auto;
            padding: 2rem;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            margin-top: 0px;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 1rem;
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div style="height: 5vh;"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="register-container">', unsafe_allow_html=True)
        
        # Centered Logo
        st.markdown('<div class="logo-container">', unsafe_allow_html=True)
        try:
            st.image("logo.png", width=120, use_column_width=False)
        except:
            st.markdown("<h1 style='text-align: center; font-size: 2.5rem; margin:0;'>🎓</h1>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
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
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                submitted = st.form_submit_button("Register", use_container_width=True)
            with col_btn2:
                if st.form_submit_button("← Back to Login", use_container_width=True):
                    st.session_state.page = 'login'
                    st.rerun()
            
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
            text-align: center;
        }
        .logo-container {
            text-align: center;
            margin-bottom: 1rem;
        }
        .stat-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)
    
    # Logo
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.image("logo.png", width=100)
    except:
        pass
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="admin-header"><h1>🔐 Admin Panel</h1><p>Manage users and view all predictions</p></div>', unsafe_allow_html=True)
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Overview", "👥 Manage Users", "📋 All Predictions"])
    
    with tab1:
        predictions_df = get_all_predictions()
        users_df = get_all_users()
        
        if not predictions_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                st.metric("Total Predictions", len(predictions_df))
                st.markdown('</div>', unsafe_allow_html=True)
            with col2:
                st.markdown('<div class="stat-card">', unsafe_allow_html=True)
                st.metric("Total Users", len(users_df))
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
        else:
            st.info("No predictions yet")
    
    with tab2:
        st.subheader("👥 Registered Users")
        users_df = get_all_users()
        
        if not users_df.empty:
            search = st.text_input("🔍 Search users", placeholder="Search by username or name...")
            if search:
                users_df = users_df[
                    users_df['username'].str.contains(search, case=False) |
                    users_df['full_name'].str.contains(search, case=False)
                ]
            
            for idx, user in users_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                with col1:
                    st.write(f"**{user['full_name']}**")
                with col2:
                    st.write(f"@{user['username']}")
                with col3:
                    st.write(user['school_name'])
                with col4:
                    st.write(user['email'] if user['email'] else "N/A")
                with col5:
                    if st.button("🗑️ Delete", key=f"del_{user['id']}"):
                        if delete_user(user['id']):
                            st.success(f"User {user['username']} deleted successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to delete user")
                st.divider()
        else:
            st.info("No users found")
    
    with tab3:
        st.subheader("📋 All Predictions")
        predictions_df = get_all_predictions()
        
        if not predictions_df.empty:
            search = st.text_input("🔍 Search predictions", placeholder="Search by username or name...", key="pred_search")
            if search:
                predictions_df = predictions_df[
                    predictions_df['username'].str.contains(search, case=False) |
                    predictions_df['full_name'].str.contains(search, case=False)
                ]
            
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
                    "created_at": st.column_config.DatetimeColumn("Registered"),
                },
                hide_index=True
            )
            
            csv = predictions_df.to_csv(index=False)
            from datetime import datetime
            st.download_button(
                label="📥 Export All Data to CSV",
                data=csv,
                file_name=f"predictions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("No predictions yet")
    
    if st.button("🚪 Logout from Admin Panel", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
