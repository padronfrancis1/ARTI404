import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go

# Define ticker symbols
tickers = {
    "NVIDIA (NVDA)": "NVDA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}

# Sidebar selection
st.sidebar.title("Select Stock")
selected_stock = st.sidebar.selectbox("Choose a stock", list(tickers.keys()))
target_stock = tickers[selected_stock]

# Fetch historical data using yfinance
st.title(f"{selected_stock} Stock Price Analysis")
st.write("Fetching historical stock data...")
try:
    stock_data = yf.Ticker(target_stock)
    hist_data = stock_data.history(period="6mo")  # Fetch the last 6 months of data
    news = stock_data.news
    if news:
        print(news)
        # for article in news:
        #     st.markdown(f"#### [{article['title']}]({article['link']})")
        #     st.write(f"Source: {article['publisher']}")
    else:
        st.write("No recent news available.")
        
    if hist_data.empty:
        st.error("No historical data found for the selected stock.")
    else:
        # Reset the index to have Date as a column
        hist_data.reset_index(inplace=True)

        # Candlestick Chart
        fig = go.Figure(
            data=[
                go.Candlestick(
                    x=hist_data['Date'],
                    open=hist_data['Open'],
                    high=hist_data['High'],
                    low=hist_data['Low'],
                    close=hist_data['Close'],
                    name='Candlestick'
                )
            ]
        )
        fig.update_layout(
            title=f"{selected_stock} Stock Price",
            xaxis_title="Date",
            yaxis_title="Price (USD)",
            xaxis_rangeslider_visible=False,
            width=1500,
            height=800
        )
        st.plotly_chart(fig, use_container_width=True)

        # Line chart
        st.markdown(f"### {selected_stock} Closing Prices")
        st.line_chart(hist_data[['Date', 'Close']].set_index('Date'))

except Exception as e:
    st.error(f"An error occurred while fetching the data: {str(e)}")

# Recent News
st.title(f"Recent News for {selected_stock}")
try:
    stock = yf.Ticker(target_stock)
    news = stock.news
    if news:
        print(news)
        # for article in news:
        #     st.markdown(f"#### [{article['title']}]({article['link']})")
        #     st.write(f"Source: {article['publisher']}")
    else:
        st.write("No recent news available.")
except Exception as e:
    st.error(f"An error occurred while fetching the news: {str(e)}")
