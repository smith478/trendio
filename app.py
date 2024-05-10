import altair as alt
import numpy as np
import pandas as pd
import streamlit as st
import yfinance as yf

# Input ticker symbol
ticker = st.text_input("Enter a ticker symbol:")

def sma_crossover(data, short_window, long_window):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()
    data['Signal'] = np.where(data['Short_MA'] > data['Long_MA'], 1, 0)
    return data

def rsi(data, window):
    delta = data['Close'].diff(1)
    up, down = delta.copy(), delta.copy()
    up[up < 0] = 0
    down[down > 0] = 0
    roll_up = up.rolling(window).mean()
    roll_down = down.rolling(window).mean().abs()
    RS = roll_up / roll_down
    RSI = 100 - (100 / (1 + RS))
    return RSI

def momentum(data, window):
    data['Momentum'] = data['Close'].pct_change(window)
    return data

# Calculate metrics
def calculate_metrics(ticker):
    data = yf.download(ticker, start='2020-01-01', end='2022-02-26')
    sma_data = sma_crossover(data, 20, 50)
    rsi_data = rsi(data, 14)
    momentum_data = momentum(data, 20)
    return sma_data, rsi_data, momentum_data

# Calculate and display metrics
sma_data, rsi_data, momentum_data = calculate_metrics(ticker)

# SMA Crossover chart
sma_chart = alt.Chart(sma_data).mark_line().encode(
    x='Date',
    y='Short_MA',
    color='Signal'
)
st.altair_chart(sma_chart, use_container_width=True)

# RSI chart
rsi_chart = alt.Chart(rsi_data).mark_line().encode(
    x='Date',
    y='RSI'
)
st.altair_chart(rsi_chart, use_container_width=True)

# Momentum chart
momentum_chart = alt.Chart(momentum_data).mark_line().encode(
    x='Date',
    y='Momentum'
)
st.altair_chart(momentum_chart, use_container_width=True)

# Recommendations
def get_recommended_stocks(tickers, sma_data, rsi_data, momentum_data):
    recommended_stocks = []
    for ticker, sma, rsi, momentum in zip(tickers, sma_data, rsi_data, momentum_data):
        # Trend following strategy:
        # Buy signal: Short MA > Long MA, RSI < 30, Momentum > 0
        # Sell signal: Short MA < Long MA, RSI > 70, Momentum < 0
        if (sma['Signal'].iloc[-1] == 1 and 
            rsi.iloc[-1] < 30 and 
            momentum['Momentum'].iloc[-1] > 0):
            recommended_stocks.append(ticker)
    return recommended_stocks

# Get a list of tickers (e.g., from a database or a file)
tickers = ["AAPL", "GOOG", "MSFT", "AMZN", "FB"]

# Calculate metrics for each ticker
sma_data_list = []
rsi_data_list = []
momentum_data_list = []
for ticker in tickers:
    sma_data, rsi_data, momentum_data = calculate_metrics(ticker)
    sma_data_list.append(sma_data)
    rsi_data_list.append(rsi_data)
    momentum_data_list.append(momentum_data)

# Get recommended stocks
recommended_stocks = get_recommended_stocks(tickers, sma_data_list, rsi_data_list, momentum_data_list)

st.write("Recommended stocks to buy:")
st.write(recommended_stocks)