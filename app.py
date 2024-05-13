import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta

# Set the page title and icon
st.set_page_config(page_title="Stock Analysis App", page_icon="📈")

# Load tickers from a CSV file
def load_tickers_from_csv(csv_file):
    try:
        tickers_df = pd.read_csv(csv_file)
        tickers = tickers_df['Ticker'].tolist()
    except FileNotFoundError:
        tickers = []
        st.warning("Tickers CSV file not found. Creating a new file.")
    return tickers

# Save tickers to a CSV file
def save_tickers_to_csv(tickers, csv_file):
    pd.DataFrame({'Ticker': tickers}).to_csv(csv_file, index=False)

# Create a sidebar
st.sidebar.header("Stock Analysis Parameters")

# Add date pickers for start and end date
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=365))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Check if the start date is before the end date
if start_date > end_date:
    st.error("Start date should be before end date.")
    st.stop()

# Load tickers from a CSV file
csv_file = "tickers.csv"
tickers = load_tickers_from_csv(csv_file)

# Add a dropdown to select a ticker
selected_ticker = st.sidebar.selectbox("Select a Ticker", tickers)

# Input field to add new ticker
new_ticker = st.sidebar.text_input("Add a new ticker (press Enter to add)")

if new_ticker:
    if new_ticker not in tickers:
        tickers.append(new_ticker)
        save_tickers_to_csv(tickers, csv_file)
        st.sidebar.success(f"{new_ticker} added successfully!")
    else:
        st.sidebar.warning(f"{new_ticker} already exists!")

# Function to calculate SMA crossover data
def sma_crossover(data, short_window, long_window):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = np.where(data['Short_MA'] > data['Long_MA'], 1, 0)
    return data

# Function to calculate RSI data
def rsi(data, window):
    delta = data['Close'].diff(1)
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean().abs()
    RS = roll_up / roll_down
    data['RSI'] = 100 - (100 / (1 + RS))
    return data

# Function to calculate momentum data
def momentum(data, window):
    data['Momentum'] = data['Close'].pct_change(window)
    return data

# Calculate metrics for the selected ticker
def calculate_metrics(ticker, start_date, end_date):
    try:
        data = yf.download(ticker, start=start_date, end=end_date)
        data_reset = data.reset_index()
        sma_data = sma_crossover(data_reset, 20, 50)
        rsi_data = rsi(data_reset, 14)
        momentum_data = momentum(data_reset, 20)
        return sma_data, rsi_data, momentum_data
    except Exception as e:
        print(f"Failed to download data for {ticker}: {str(e)}")
        return None, None, None

# Calculate and display metrics for the selected ticker
if selected_ticker:
    sma_data, rsi_data, momentum_data = calculate_metrics(selected_ticker, start_date, end_date)

    if sma_data is not None:
        # SMA Crossover chart
        sma_chart = alt.Chart(sma_data).mark_line().encode(
            x='Date',
            y='Short_MA',
            color='Signal'
        )
        st.altair_chart(sma_chart, use_container_width=True)

    if rsi_data is not None:
        # RSI chart
        rsi_chart = alt.Chart(rsi_data).mark_line().encode(
            x='Date',
            y='RSI'
        )
        st.altair_chart(rsi_chart, use_container_width=True)

    if momentum_data is not None:
        # Momentum chart
        momentum_chart = alt.Chart(momentum_data).mark_line().encode(
            x='Date',
            y='Momentum'
        )
        st.altair_chart(momentum_chart, use_container_width=True)

# Recommendations
def get_recommended_stocks(tickers, start_date, end_date):
    recommended_stocks_to_buy = []
    recommended_stocks_to_sell = []

    for ticker in tickers:
        sma_data, rsi_data, momentum_data = calculate_metrics(ticker, start_date, end_date)

        if sma_data is not None and rsi_data is not None and momentum_data is not None:
            # Buy signal: Short MA > Long MA, RSI < 30, Momentum > 0
            if (sma_data['Signal'].iloc[-1] == 1 and 
                rsi_data['RSI'].iloc[-1] < 30 and 
                momentum_data['Momentum'].iloc[-1] > 0):
                recommended_stocks_to_buy.append(ticker)

            # Sell signal: Short MA < Long MA, RSI > 70, Momentum < 0
            if (sma_data['Signal'].iloc[-1] == 0 and 
                rsi_data['RSI'].iloc[-1] > 70 and 
                momentum_data['Momentum'].iloc[-1] < 0):
                recommended_stocks_to_sell.append(ticker)

    return recommended_stocks_to_buy, recommended_stocks_to_sell

# Calculate metrics for each ticker and get recommendations
recommended_stocks_to_buy, recommended_stocks_to_sell = get_recommended_stocks(tickers, start_date, end_date)

st.write("Recommended stocks to buy:")
st.write(recommended_stocks_to_buy)

st.write("Recommended stocks to sell:")
st.write(recommended_stocks_to_sell)