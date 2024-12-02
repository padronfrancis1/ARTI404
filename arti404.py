import streamlit as st
import pandas as pd
import yfinance as yf
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

# Sidebar
st.sidebar.title("Select Stock")
selected_stock = st.sidebar.selectbox("Choose a stock", list(tickers.keys()))
target_stock = tickers[selected_stock]

st.title(f"{selected_stock} Stock Price Analysis")

try:
    stock_data = yf.Ticker(target_stock)
    hist_data = stock_data.history(period="6mo")

    news = stock_data.news

    if news:
    for article in news:
        st.markdown(f"#### [{article['title']}]({article['link']})")
        st.text(f"Source: {article['publisher']}")
    else:
        st.write("No recent news available.")

    if hist_data.empty:
        st.error(f"No historical data found for {target_stock}")
    else:
        hist_data.reset_index(inplace=True)
        hist_data['Month'] = hist_data['Date'].dt.month
        hist_data['Days'] = (hist_data['Date'] - hist_data['Date'].min()).dt.days

        X = hist_data[['Days']]
        y = hist_data['Close']   # Target: Closing prices

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        regressor.fit(X_train, y_train)

        hist_data['predicted_price'] = regressor.predict(X)
        hist_data['Visible_Close'] = hist_data.apply(
            lambda row: row['Close'] if row['Month'] not in [8, 9] else np.nan, axis=1
        )
        aug_sep_data = hist_data[hist_data['Month'].isin([8, 9])].copy()
        aug_sep_data['predicted_price'] = regressor.predict(aug_sep_data[['Days']])
        last_day = hist_data['Days'].max()
        future_days = np.array([[last_day + i] for i in range(1, 31)])
        predictions = regressor.predict(future_days)
        future_dates = pd.date_range(hist_data['Date'].max(), periods=31, freq='D')[1:]
        prediction_df = pd.DataFrame({
            'Date': future_dates,
            'Predicted Price': predictions
        })

        # Plotting
        sns.set(style="whitegrid")
        fig, ax = plt.subplots(figsize=(10, 6))

        sns.lineplot(x='Date', y='Visible_Close', data=hist_data, label='Original (Visible)', ax=ax, color='blue', linewidth=1.5)
        sns.lineplot(x='Date', y='predicted_price', data=aug_sep_data, label='Model Predictions (Aug-Sep)', ax=ax, color='orange', linestyle='--', linewidth=2)
        sns.scatterplot(x='Date', y='Close', data=aug_sep_data, label='Actual (Aug-Sep)', ax=ax, color='green', s=40, alpha=0.8)
        sns.lineplot(x='Date', y='Predicted Price', data=prediction_df, label='Future Predictions', ax=ax, color='red', linewidth=2)
        # Customize the plot
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price', fontsize=12)
        ax.set_title(f'{selected_stock} Predictions with Hidden Actual Data (Aug-Sep)', fontsize=16)
        ax.legend(fontsize=10, loc='upper left')
        ax.grid(visible=True, linestyle='--', alpha=0.5)
        # Display the plot in Streamlit
        st.pyplot(fig)

except Exception as e:
    st.error(f"An error occurred while fetching the data: {str(e)}")
