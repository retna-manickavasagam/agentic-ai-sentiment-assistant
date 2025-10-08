def admin_dashboard():
    st.title("Admin Dashboard")
    
    # Login check
    if not st.session_state.logged_in:
        with st.form(key='login_form'):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_button = st.form_submit_button("Login")
            
            if login_button:
                if username in st.session_state.users and st.session_state.users[username] == password:
                    st.session_state.logged_in = True
                    st.success("Logged in successfully!")
                else:
                    st.error("Invalid credentials")
        return

    # Admin features
    st.header("User Management")
    with st.form(key='user_management'):
        new_user = st.text_input("New Username")
        new_password = st.text_input("New Password", type="password")
        add_user = st.form_submit_button("Add User")
        
        if add_user and new_user and new_password:
            st.session_state.users[new_user] = new_password
            st.success(f"User {new_user} added successfully!")
         
    st.header("Chat History")
    if st.session_state.chat_history:
        df = pd.DataFrame(st.session_state.chat_history)
        st.dataframe(df[['timestamp', 'message', 'response', 'sentiment']])
        
        if st.button("Clear Chat History"):
            st.session_state.chat_history = []
            st.success("Chat history cleared!")
