# Streamlit chat UI (user view)

import streamlit as st
from components.chat_ui import chatbot_ui
import openai
import plotly.express as px
import pandas as pd
from datetime import datetime
from streamlit_option_menu import option_menu
from textblob import TextBlob
import requests
import plotly.graph_objects as go
import numpy as np


# Set page config for wide layout and robot favicon
st.set_page_config(
    page_title="Sent AI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)
# FastAPI backend URL
API_BASE_URL = "http://localhost:8000"

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
             margin-top: 20px;
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

try:
    openai.api_key = st.secrets["openai"]    
except:
    st.error("🚨 OpenAI API key not found in secrets.toml. Add it as per instructions!")
    st.stop()

# Knowledge base (customize as needed)
KNOWLEDGE_BASE = "You are a friendly assistant for a tech company building AI tools like Grok. Provide clear, concise answers with a touch of humor"

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
    st.markdown('<h1 class="main-header">🤖 Sent AI Shopping Assistant</h1>', unsafe_allow_html=True)
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
####---------------------------------------------------------------------------------------
# Page: Sentiment View
elif selected == "📊 Sentiment":

    def call_api(endpoint, params=None):
        """Helper function to call FastAPI endpoints"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, params=params)
            if response.status_code == 200:
                return response.json()
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
                return None
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the backend API. Make sure FastAPI is running on localhost:8000")
            return None

    def get_sentiment_stats(product_id=None):
        """Get sentiment statistics"""
        params = {"product_id": product_id} if product_id else {}
        return call_api("/sentiment_stats", params)

    def get_sentiments_by_label(label, limit=100):
        """Get sentiments by label"""
        return call_api(f"/sentiments/filter/by-label/", {"label": label, "limit": limit})

    def get_available_products():
        """Get available product IDs"""
        return call_api("/get_product_ids", {"limit": 50})

    def get_available_labels():
        """Get available sentiment labels"""
        return call_api("/available-sentiment-labels")

    def generate_business_advice(stats, product_id=None):
        """Generate business advice based on sentiment statistics"""
        total_reviews = stats.get('total_reviews', 0)
        avg_sentiment = stats.get('average_sentiment', 0)
        positive_pct = (stats.get('positive_reviews', 0) / total_reviews * 100) if total_reviews > 0 else 0
        negative_pct = (stats.get('negative_reviews', 0) / total_reviews * 0) if total_reviews > 0 else 0
        
        advice = []
        
        if total_reviews == 0:
            return ["📝 No reviews available for analysis"]
        
        # Overall performance
        if avg_sentiment > 0.7:
            advice.append("🎉 Excellent customer satisfaction! Keep up the great work.")
        elif avg_sentiment > 0.3:
            advice.append("👍 Good performance with room for improvement.")
        else:
            advice.append("⚠️ Need immediate attention to improve customer experience.")
        
        # Positive reviews analysis
        if positive_pct > 80:
            advice.append("💫 High positive review rate indicates strong product-market fit.")
        elif positive_pct < 50:
            advice.append("🔍 Low positive reviews suggest areas for product improvement.")
        
        # Negative reviews analysis
        if negative_pct > 30:
            advice.append("🚨 High negative reviews detected. Investigate common complaints.")
        
        # Volume analysis
        if total_reviews < 10:
            advice.append("📊 Consider collecting more reviews for better insights.")
        elif total_reviews > 100:
            advice.append("📈 Strong review volume provides reliable insights.")
        
        return advice

    # Main App
    def main():
        st.title("📊 Sentiment Analysis Dashboard")
        st.markdown("---")
        
        # Sidebar for filters
        st.sidebar.header("🔍 Filters")
        
        # Get available data
        products_data = get_available_products()
        labels_data = get_available_labels()
        
        # Product filter
        product_options = ["All Products"]
        if products_data and 'product_ids' in products_data:
            product_options.extend(products_data['product_ids'])
        
        selected_product = st.sidebar.selectbox(
            "Select Product:",
            product_options,
            index=0
        )
        
        # Sentiment label filter
        label_options = ["All Sentiments"]
        if labels_data and 'available_labels' in labels_data:
            label_options.extend([label['label'] for label in labels_data['available_labels']])
        
        selected_label = st.sidebar.selectbox(
            "Filter by Sentiment:",
            label_options,
            index=0
        )
        
        # Number of reviews to display
        review_limit = st.sidebar.slider(
            "Number of reviews to display:",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )
        
        # Main content area
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("📈 Sentiment Statistics")
            
            # Get sentiment stats
            product_id = None if selected_product == "All Products" else selected_product
            stats_data = get_sentiment_stats(product_id)
            
            if stats_data and 'total_reviews' in stats_data:
                # Display KPI cards
                kpi1, kpi2, kpi3, kpi4 = st.columns(4)
                
                with kpi1:
                    st.metric(
                        label="Total Reviews",
                        value=stats_data['total_reviews'],
                        delta=None
                    )
                
                with kpi2:
                    sentiment_score = stats_data.get('average_sentiment', 0)
                    st.metric(
                        label="Avg. Sentiment Score",
                        value=f"{sentiment_score:.2f}",
                        delta=None
                    )
                
                with kpi3:
                    positive_pct = (stats_data.get('positive_reviews', 0) / stats_data['total_reviews'] * 100) if stats_data['total_reviews'] > 0 else 0
                    st.metric(
                        label="Positive Reviews",
                        value=f"{positive_pct:.1f}%",
                        delta=None
                    )
                
                with kpi4:
                    negative_pct = (stats_data.get('negative_reviews', 0) / stats_data['total_reviews'] * 100) if stats_data['total_reviews'] > 0 else 0
                    st.metric(
                        label="Negative Reviews",
                        value=f"{negative_pct:.1f}%",
                        delta=None
                    )
                
                # Create sentiment distribution chart
                if stats_data['total_reviews'] > 0:
                    sentiment_data = {
                        'Sentiment': ['Positive', 'Negative', 'Neutral'],
                        'Count': [
                            stats_data.get('positive_reviews', 0),
                            stats_data.get('negative_reviews', 0),
                            stats_data.get('neutral_reviews', 0)
                        ]
                    }
                    
                    df_sentiment = pd.DataFrame(sentiment_data)
                    
                    fig_pie = px.pie(
                        df_sentiment,
                        values='Count',
                        names='Sentiment',
                        title='Sentiment Distribution',
                        color='Sentiment',
                        color_discrete_map={
                            'Positive': "#0a7d0a",
                            'Negative': "#ec3e3e", 
                            'Neutral': "#dddd64fd"
                        }
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
            else:
                st.warning("No statistics data available")
        
        with col2:
            st.subheader("💡 Business Advice")
            
            if stats_data and 'total_reviews' in stats_data:
                advice_list = generate_business_advice(stats_data, product_id)
                
                for advice in advice_list:
                    st.info(advice)
            else:
                st.info("Select a product to see business recommendations")
        
        # Detailed Reviews Section
        st.markdown("---")
        st.subheader("📝 Detailed Reviews")
        
        if selected_label != "All Sentiments":
            # Get filtered reviews
            reviews_data = get_sentiments_by_label(selected_label, review_limit)
            
            if reviews_data and 'data' in reviews_data and reviews_data['data']:
                # Convert to DataFrame for display
                reviews_list = []
                for review in reviews_data['data']:
                    reviews_list.append({
                        'Product ID': review.get('product_id', 'N/A'),
                        'Review Text': review.get('reviews_text', 'N/A'),
                        'Rating': review.get('reviews_rating', 'N/A'),
                        'Sentiment': review.get('sentiment_label', 'N/A'),
                        'Sentiment Score': f"{float(review.get('sentiment_score', 0)):.2f}" if review.get('sentiment_score') else 'N/A',
                        'Title': review.get('reviews_title', 'N/A'),
                        'User': review.get('reviews_username', 'Anonymous')
                    })
                
                df_reviews = pd.DataFrame(reviews_list)
                
                # Display reviews in an expandable table
                with st.expander(f"📋 Show {len(df_reviews)} {selected_label} Reviews", expanded=True):
                    st.dataframe(
                        df_reviews,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Review Text": st.column_config.TextColumn(width="large"),
                            "Title": st.column_config.TextColumn(width="medium"),
                        }
                    )
                
                # Show sample review cards
                st.subheader("🎯 Sample Reviews")
                sample_reviews = reviews_data['data'][:3]  # Show first 3 reviews
                
                for i, review in enumerate(sample_reviews):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            sentiment_color = {
                                'positive': 'green',
                                'negative': 'red',
                                'neutral': 'gray'
                            }.get(review.get('sentiment_label', 'neutral'), 'gray')
                            
                            st.markdown(f"""
                            <div style="padding: 10px; border-left: 4px solid {sentiment_color}; background-color: #f0f2f6; margin: 5px 0; color: black">
                                <strong>{review.get('reviews_title', 'No Title')}</strong><br>
                                {review.get('reviews_text', 'No content')}<br>
                                <small>Rating: {review.get('reviews_rating', 'N/A')} | 
                                Sentiment: <span style="color: {sentiment_color}">{review.get('sentiment_label', 'N/A')}</span></small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            sentiment_score = float(review.get('sentiment_score', 0))
                            st.metric("Confidence", f"{sentiment_score:.2f}")
            
            else:
                st.warning(f"No {selected_label} reviews found")
        
        else:
            st.info("Select a specific sentiment label to view detailed reviews")

        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: gray;'>"
            "Sentiment Analysis Dashboard • Powered by FastAPI & Streamlit"
            "</div>",
            unsafe_allow_html=True
        )

    if __name__ == "__main__":
        main()
    
    st.markdown('</div>', unsafe_allow_html=True)

