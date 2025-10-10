import streamlit as st
# Set page configuration

def chatbot_ui():
    st.title("Chatbot Interface")


    # Chat container
    chat_container = st.container()
        
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

    
  
    # Chat input
    if prompt := st.chat_input("Ask me anything! 🤖"):
        st.session_state.messages.append({"content": prompt, "is_user": True})
        message(prompt, is_user=True)
        
        # Generate bot response
        with st.chat_message("assistant"):
            with st.spinner("🤖 Thinking..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": KNOWLEDGE_BASE},
                            *[{"role": "user" if m["is_user"] else "assistant", "content": m["content"]} for m in st.session_state.messages]
                        ]
                    )
                    bot_reply = response.choices[0].message.content
                    st.session_state.messages.append({"content": bot_reply, "is_user": False})
                    message(bot_reply, is_user=False)
                    
                    # Store for analysis
                    st.session_state.chat_history.append({
                        "timestamp": datetime.now(),
                        "user": prompt,
                        "bot": bot_reply
                    })
                except Exception as e:
                    st.error(f"🤖 Oops! Error: {e}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", key="clear_chat"):
        st.session_state.messages = []
        st.experimental_rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)