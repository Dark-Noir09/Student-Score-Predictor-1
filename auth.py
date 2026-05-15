import streamlit as st
from database import login_user, register_user, get_all_predictions, get_all_users, delete_user
from datetime import datetime

def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'page' not in st.session_state:
        st.session_state.page = 'login'
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = False

def login_page():
    # Remove default Streamlit padding and headers
    st.markdown("""
        <style>
        .main .block-container { padding-top: 0rem !important; }
        header[data-testid="stHeader"] { display: none !important; }
        #MainMenu, footer { visibility: hidden !important; }
        </style>
    """, unsafe_allow_html=True)
    
    # Add space at top
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Center everything using columns
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Logo - centered using st.image with use_container_width=False, but inside column it centers
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='text-align: center;'>🎓</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #667eea;'>Student Score Predictor</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Login to access your dashboard</p>", unsafe_allow_html=True)
        
        username = st.text_input("Username", placeholder="Enter your username", label_visibility="collapsed")
        password = st.text_input("Password", type="password", placeholder="Enter your password", label_visibility="collapsed")
        
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

def register_page():
    st.markdown("""
        <style>
        .main .block-container { padding-top: 0rem !important; }
        header { display: none !important; }
        footer { visibility: hidden !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", width=100)
        except:
            st.markdown("<h1 style='text-align: center;'>🎓</h1>", unsafe_allow_html=True)
        
        st.markdown("<h2 style='text-align: center; color: #667eea;'>📝 Create Account</h2>", unsafe_allow_html=True)
        
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
                if not all([full_name, username, password, school_name]):
                    st.error("Please fill all required fields (*)")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 4:
                    st.error("Password must be at least 4 characters")
                else:
                    success, msg = register_user(username, password, full_name, school_name, grade, email)
                    if success:
                        st.success(msg)
                        st.balloons()
                        st.info("Please login with your credentials")
                        st.session_state.page = 'login'
                        st.rerun()
                    else:
                        st.error(msg)

def admin_panel():
    st.markdown("""
        <style>
        .admin-header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 10px; color: white; text-align: center; }
        .stat-card { background: white; padding: 1rem; border-radius: 10px; text-align: center; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        </style>
    """, unsafe_allow_html=True)
    
    # Logo centered
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        try:
            st.image("logo.png", width=80)
        except:
            st.markdown("<h1 style='text-align: center;'>🎓</h1>", unsafe_allow_html=True)
    
    st.markdown('<div class="admin-header"><h1>🔐 Admin Panel</h1><p>Manage users and view all predictions</p></div>', unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard Overview", "👥 Manage Users", "📋 All Predictions"])
    
    with tab1:
        pred_df = get_all_predictions()
        users_df = get_all_users()
        if not pred_df.empty:
            c1, c2, c3, c4 = st.columns(4)
            with c1: st.metric("Total Predictions", len(pred_df))
            with c2: st.metric("Total Users", len(users_df))
            with c3: st.metric("Average Score", f"{pred_df['predicted_score'].mean():.1f}")
            with c4: st.metric("High Scorers (90+)", len(pred_df[pred_df['predicted_score']>=90]))
        else:
            st.info("No predictions yet")
    
    with tab2:
        st.subheader("👥 Registered Users")
        users_df = get_all_users()
        if not users_df.empty:
            search = st.text_input("🔍 Search users", placeholder="Search by username or name...")
            if search:
                users_df = users_df[users_df['username'].str.contains(search, case=False) | users_df['full_name'].str.contains(search, case=False)]
            for _, user in users_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
                col1.write(f"**{user['full_name']}**")
                col2.write(f"@{user['username']}")
                col3.write(user['school_name'])
                col4.write(user['email'] if user['email'] else "N/A")
                if col5.button("🗑️ Delete", key=f"del_{user['id']}"):
                    if delete_user(user['id']):
                        st.success(f"User {user['username']} deleted")
                        st.rerun()
                    else:
                        st.error("Failed")
                st.divider()
        else:
            st.info("No users found")
    
    with tab3:
        st.subheader("📋 All Predictions")
        pred_df = get_all_predictions()
        if not pred_df.empty:
            search = st.text_input("🔍 Search predictions", placeholder="Search...", key="pred_search")
            if search:
                pred_df = pred_df[pred_df['username'].str.contains(search, case=False) | pred_df['full_name'].str.contains(search, case=False)]
            st.dataframe(pred_df, use_container_width=True, hide_index=True)
            csv = pred_df.to_csv(index=False)
            st.download_button("📥 Export All Data to CSV", data=csv, file_name=f"predictions_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", mime="text/csv", use_container_width=True)
        else:
            st.info("No predictions yet")
    
    if st.button("🚪 Logout from Admin Panel", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.rerun()
