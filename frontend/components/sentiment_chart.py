def sentiment_view():
    st.title("Sentiment Analysis View")
    
    if not st.session_state.chat_history:
        st.warning("No chat history available")
        return

    # Prepare data for visualization
    df = pd.DataFrame(st.session_state.chat_history)
    sentiment_counts = df['sentiment'].value_counts()
    
    # Sentiment distribution chart
    st.header("Sentiment Distribution")
    fig = px.pie(values=sentiment_counts.values, 
                 names=sentiment_counts.index,
                 title="Sentiment Distribution of Messages")
    st.plotly_chart(fig)
    
    # Sentiment over time
    st.header("Sentiment Over Time")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    fig_time = px.line(df, x='timestamp', y='sentiment',
                      title="Sentiment Trend Over Time")
    st.plotly_chart(fig_time)
    
    # Detailed view
    st.header("Detailed Messages")
    sentiment_filter = st.selectbox("Filter by sentiment", 
                                  ["All", "Positive", "Negative", "Neutral"])
    
    filtered_df = df if sentiment_filter == "All" else df[df['sentiment'] == sentiment_filter]
    st.dataframe(filtered_df[['timestamp', 'message', 'sentiment']])

if __name__ == "__main__":
    main()
