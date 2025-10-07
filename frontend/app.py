# Streamlit chat UI (user view)

import streamlit as st
from components.chat_ui import chatbot_ui

st.title("🛒 Agentic AI Sentiment Assistant")
st.write("Chat with the shopping assistant!")

def main():
    chatbot_ui()

if __name__ == "__main__":
    main()

