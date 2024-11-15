import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import yfinance as yf
from newspaper import Article
import matplotlib.pyplot as plt
import plotly.graph_objs as go

tickers = {
    "NVIDIA (NVDA)": "NVDA",
    "Apple (AAPL)": "AAPL",
    "Tesla (TSLA)": "TSLA"
}
 
st.sidebar.title("Select Stock")
selected_stock = st.sidebar.selectbox("Choose a stock", list(tickers.keys()))
target_stock = tickers[selected_stock]
page_url=f'https://ca.finance.yahoo.com/quote/{target_stock}/history/'
print(page_url)
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=chrome_options)
driver.get(page_url)
soup = BeautifulSoup(driver.page_source, 'html.parser')
driver.close()
table = soup.find('table')
headers = [header.text.strip() for header in table.find_all('th')]
rows = table.find_all('tr')
data = []
for row in rows[1:]:
    cells = row.find_all('td')
    if len(cells) >= 5:
        data.append([cell.text.strip() for cell in cells])

df = pd.DataFrame(data, columns=headers)
df.rename(columns={'Close    Close price adjusted for splits.': 'Close'}, inplace=True)

df['Date'] = pd.to_datetime(df['Date'], format='%b %d, %Y')
df['Close'] = df['Close'].astype(float)

# Historical Data
st.markdown('<div style="width: 80%;overflow-y: scroll;overflow-x: scroll;">', unsafe_allow_html=True)

# Streamlit line Chart
# st.line_chart(data=df, x='Date',y='Close')

fig = go.Figure(
    data=[
        go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
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
st.markdown('</div>', unsafe_allow_html=True)

# News
st.title(f"Recent News for {target_stock}")
stock = yf.Ticker(target_stock)
news = stock.news
if news:
    st.markdown('<div style="width: 40%;overflow-y: scroll;overflow-x: scroll;">', unsafe_allow_html=True)
    for article in news:
        st.subheader(article['title'])
        st.write(f"Source: {article['publisher']}")
        st.write(f"[Read more]({article['link']})")
    st.markdown("</div>", unsafe_allow_html=True)
else:
    st.write("No recent news available.")
