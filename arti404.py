import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import seaborn as sns
import matplotlib.pyplot as plt

regressor = LinearRegression()
tickers = {
    "NVIDIA (NVDA)": "NVDA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}

st.sidebar.title("Select Stock")
selected_stock = st.sidebar.selectbox("Choose a stock", list(tickers.keys()))
target_stock = tickers[selected_stock]

st.title(f"{selected_stock} Stock Price Analysis")
try:
    stock_data = yf.Ticker(target_stock)
    hist_data = stock_data.history(period="6mo")
    news = stock_data.news

    if hist_data.empty:
        st.error("No historical data found for {target_stock}")
    else:
        hist_data.reset_index(inplace=True)

        # Convert Date to numeric (days since the first date)
        hist_data['Days'] = (hist_data['Date'] - hist_data['Date'].min()).dt.days

        # Define features and target
        X = hist_data[['Days']]  # Input feature: Days since start
        y = hist_data['Close']   # Target: Closing prices

        # Train-test split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        
        # Train the Linear Regression model
        regressor.fit(X_train, y_train)


        # Predict actual data
        hist_data['predicted_price'] = regressor.predict(hist_data[['Days' ]])


        # Predict future stock prices for the next 30 days
        last_day = hist_data['Days'].max()
        future_days = np.array([[last_day + i] for i in range(1, 31)])
        predictions = regressor.predict(future_days)

        # Generate future dates for predictions
        future_dates = pd.date_range(hist_data['Date'].max(), periods=31, freq='D')[1:]
        prediction_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Price': predictions
        })

        # Assuming hist_data and prediction_df are defined
        sns.set(style="whitegrid")

        # Create the plot
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(x='Date', y='Close', data=hist_data, label='Original', ax=ax)
        sns.lineplot(x='Date', y='Predicted Price', data=prediction_df, label='Predicted', ax=ax)
        sns.lineplot(x='Date', y='predicted_price', data=hist_data, label='Algorithm', ax=ax)
        ax.set_xlabel('Date')
        ax.set_ylabel('Price')
        ax.set_title('Predictions')
        ax.legend()

        # Display the plot in Streamlit
        st.pyplot(fig)

        # # Line chart
        # st.markdown(f"### {selected_stock} Closing Prices")
        # st.line_chart(hist_data[['Date', 'Close']].set_index('Date'))
    if news:
        for article in news:
            st.markdown(f"#### [{article['title']}]({article['link']})")
            st.text(f"Source: {article['publisher']}")
    else:
        st.write("No recent news available.")

except Exception as e:
    st.error(f"An error occurred while fetching the data: {str(e)}")
