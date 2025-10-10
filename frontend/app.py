# Streamlit chat UI (user view)

import streamlit as st
from components.chat_ui import chatbot_ui
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu

# Set page config for wide layout and robot favicon
st.set_page_config(
    page_title="Sent AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for colorful UI with hover effects
st.markdown("""
    <style>
    .main-header {
        color: #FF4B91; 
        font-size: 2.5rem; 
        text-align: center; 
        margin-bottom: 1.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .chat-container {
        background: linear-gradient(135deg, #6B7280 0%, #4B5563 100%); 
        padding: 2rem; 
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .admin-container {
        background: linear-gradient(135deg, #FCD34D 0%, #F59E0B 100%); 
        padding: 2rem; 
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .sentiment-container {
        background: linear-gradient(135deg, #34D399 0%, #059669 100%); 
        padding: 2rem; 
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: white; 
        padding: 1rem; 
        border-radius: 10px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: scale(1.05);
    }
    .stButton>button {
        background-color: #FF4B91;
        color: white;
        border-radius: 8px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #DB2777;
        transform: translateY(-2px);
    }
    .sidebar .stSelectbox {
        background: #4B5563;
        color: white;
        border-radius: 8px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation with robot emojis
with st.sidebar:
    st.markdown("### 🤖 Chatbot App")
    selected = option_menu(
        menu_title=None,
        options=["💬 Chat", "🔧 Admin", "📊 Sentiment"],
        icons=["chat-dots-fill", "gear-fill", "graph-up"],
        menu_icon="robot",
        default_index=0,
        styles={
            "container": {"background-color": "#1F2937", "padding": "10px", "border-radius": "10px"},
            "icon": {"color": "#FF4B91", "font-size": "20px"},
            "nav-link": {"color": "white", "font-size": "16px", "--hover-color": "#FF4B91"},
            "nav-link-selected": {"background-color": "#FF4B91"}
        }
    )

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # Store {'user': msg, 'bot': msg, 'timestamp': dt}

# Page: Chatbot
if selected == "💬 Chat":
    st.markdown('<h1 class="main-header">🤖 Sent AI Interface</h1>', unsafe_allow_html=True)
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Display chat history
    for i, msg in enumerate(st.session_state.messages):
        message(msg["content"], is_user=msg["is_user"], key=f"msg_{i}")
    
    # Chat input
    if prompt := st.chat_input("Ask me anything!🚀🤖"):
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

# Page: Admin Dashboard
elif selected == "🔧 Admin":
    st.markdown('<h1 class="main-header">🔧 Admin Dashboard 🤖</h1>', unsafe_allow_html=True)
    st.markdown('<div class="admin-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        df = pd.DataFrame(st.session_state.chat_history)
        
        # Interactive metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("💬 Total Messages", len(df))
            st.markdown('</div>', unsafe_allow_html=True)
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("📏 Avg User Msg Length", f"{df['user'].str.len().mean():.1f} chars")
            st.markdown('</div>', unsafe_allow_html=True)
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric("🤖 Bot Responses", len(df["bot"].dropna()))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Filter by date
        st.subheader("📅 Filter Conversations")
        date_range = st.slider("Select Date Range", 
                              min_value=df["timestamp"].min().date(), 
                              max_value=df["timestamp"].max().date(), 
                              value=(df["timestamp"].min().date(), df["timestamp"].max().date()),
                              format="YYYY-MM-DD")
        filtered_df = df[df["timestamp"].dt.date.between(date_range[0], date_range[1])]
        
        # Conversation table
        st.subheader("📋 Recent Conversations")
        st.dataframe(filtered_df[["timestamp", "user", "bot"]], use_container_width=True)
        
        # Download button
        csv = filtered_df.to_csv(index=False)
        st.download_button("📥 Download Filtered Data", csv, "chat_history.csv", "text/csv")
    
    else:
        st.info("🤖 Start chatting to see data here!")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Page: Sentiment View
elif selected == "📊 Sentiment":
    st.markdown('<h1 class="main-header">📊 Sentiment Analysis 🤖</h1>', unsafe_allow_html=True)
    st.markdown('<div class="sentiment-container">', unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        df = pd.DataFrame(st.session_state.chat_history)
        df["sentiment"] = df["user"].apply(lambda x: TextBlob(x).sentiment.polarity)
        df["label"] = df["sentiment"].apply(lambda x: "Positive" if x > 0.1 else ("Negative" if x < -0.1 else "Neutral"))
        
        # Interactive pie chart
        fig_pie = px.pie(df, names="label", title="Sentiment Distribution",
                         color="label", color_discrete_map={"Positive": "#34D399", "Negative": "#EF4444", "Neutral": "#FBBF24"})
        fig_pie.update_traces(textinfo="percent+label", hovertemplate="%{label}: %{percent}")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Sentiment trend line
        fig_line = px.line(df, x="timestamp", y="sentiment", color="label", title="Sentiment Over Time",
                          color_discrete_map={"Positive": "#34D399", "Negative": "#EF4444", "Neutral": "#FBBF24"})
        fig_line.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_line, use_container_width=True)
        
        # Sentiment threshold slider
        st.subheader("🎚️ Adjust Sentiment Threshold")
        threshold = st.slider("Positive/Negative Threshold", 0.05, 0.5, 0.1, 0.05)
        df["label"] = df["sentiment"].apply(lambda x: "Positive" if x > threshold else ("Negative" if x < -threshold else "Neutral"))
        
        # Summary stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("😊 Positive", f"{(len(df[df['label']=='Positive'])/len(df)*100):.1f}%")
        with col2:
            st.metric("😔 Negative", f"{(len(df[df['label']=='Negative'])/len(df)*100):.1f}%")
        with col3:
            st.metric("😐 Neutral", f"{(len(df[df['label']=='Neutral'])/len(df)*100):.1f}%")
    
    else:
        st.info("🤖 Chat first to analyze sentiments!")
    
    st.markdown('</div>', unsafe_allow_html=True)

