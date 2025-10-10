# Page: Sentiment View
if __name__ == "__main__":
    elif selected == "Sentiment View 📈":
    st.markdown('<div class="title">📈 Sentiment Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Visualize user sentiment over time 😊😐😞</div>', unsafe_allow_html=True)

    if st.session_state.sentiment_data:
        sentiment_df = pd.DataFrame(st.session_state.sentiment_data)
        
        # Sentiment Distribution Pie Chart
        st.markdown("### Sentiment Distribution")
        sentiment_counts = sentiment_df['sentiment'].value_counts().reset_index()
        sentiment_counts.columns = ['Sentiment', 'Count']
        fig_pie = px.pie(sentiment_counts, names='Sentiment', values='Count', color='Sentiment',
                         color_discrete_map={'Positive 😊': '#27ae60', 'Neutral 😐': '#f1c40f', 'Negative 😞': '#e74c3c'})
        st.plotly_chart(fig_pie, use_container_width=True)

        # Sentiment Score Over Time
        st.markdown("### Sentiment Trend")
        fig_line = px.line(sentiment_df, x='timestamp', y='score', title="Sentiment Score Over Time",
                           labels={'score': 'Sentiment Score', 'timestamp': 'Time'},
                           color_discrete_sequence=['#ff6f61'])
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.info("No sentiment data available yet. Start chatting to see insights! 📊")
