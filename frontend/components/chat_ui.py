import streamlit as st
# Set page configuration

st.set_page_config(page_title="Chatbot Dashboard", layout="wide")

# Initialize session state for chat history and user management
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'users' not in st.session_state:
    st.session_state.users = {'admin': 'password123'}
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Simulated sentiment analysis function
def analyze_sentiment(message):
    # Placeholder for sentiment analysis logic
    words = message.lower().split()
    positive_words = ['good', 'great', 'awesome', 'happy']
    negative_words = ['bad', 'poor', 'terrible', 'sad']
    
    pos_count = sum(1 for word in words if word in positive_words)
    neg_count = sum(1 for word in words if word in negative_words)
    
    if pos_count > neg_count:
        return 'Positive'
    elif neg_count > pos_count:
        return 'Negative'
    return 'Neutral'

# Chatbot response simulation
def get_bot_response(user_input):
    return f"Bot: Echoing your message - {user_input}"

# Main app
def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Chatbot", "Admin Dashboard", "Sentiment View"])

    if page == "Chatbot":
        chatbot_ui()
    elif page == "Admin Dashboard":
        admin_dashboard()
    elif page == "Sentiment View":
        sentiment_view()

def chatbot_ui():
    st.title("Chatbot Interface")
    
    # Chat container
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for chat in st.session_state.chat_history:
            st.markdown(f"**User**: {chat['message']}")
            st.markdown(f"**Bot**: {chat['response']}")
            st.markdown(f"**Sentiment**: {chat['sentiment']}")
            st.markdown("---")
    
    # Input form
    with st.form(key='chat_form', clear_on_submit=True):
        user_input = st.text_input("Type your message:", key="user_input")
        submit_button = st.form_submit_button("Send")
        
        if submit_button and user_input:
            response = get_bot_response(user_input)
            sentiment = analyze_sentiment(user_input)
            st.session_state.chat_history.append({
                'message': user_input,
                'response': response,
                'sentiment': sentiment,
                'timestamp': datetime.now()
            })
