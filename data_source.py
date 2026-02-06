import streamlit as st
import yfinance as yf
import pandas as pd

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_stock_data(symbol):
    """
    Fetch stock data from yfinance. Handles fundamentals and history.
    Gracefully falls back for missing data.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        history = ticker.history(period="1y", interval="1d")
        
        # Fetch financial statements
        income = ticker.get_income_stmt()
        balance = ticker.get_balance_sheet()

        data = {}
        data['price'] = info.get('currentPrice')
        data['market_cap'] = info.get('marketCap')
        data['volume'] = info.get('volume')
        data['pe'] = info.get('trailingPE')
        data['pbv'] = info.get('priceToBook')
        data['eps'] = info.get('trailingEps')
        data['roe'] = info.get('returnOnEquity')
        data['debt_equity'] = info.get('debtToEquity')

        # Revenue growth (last year vs previous)
        if not income.empty and 'Total Revenue' in income.index and len(income.columns) >= 2:
            revenues = income.loc['Total Revenue']
            data['revenue_growth'] = ((revenues[income.columns[0]] - revenues[income.columns[1]]) / revenues[income.columns[1]]) * 100 if revenues[income.columns[1]] != 0 else None

        # Net profit margin
        if not income.empty and 'Net Income' in income.index and 'Total Revenue' in income.index:
            net_income = income.loc['Net Income', income.columns[0]]
            revenue = income.loc['Total Revenue', income.columns[0]]
            data['net_margin'] = (net_income / revenue) * 100 if revenue != 0 else None

        return data, history
    except Exception as e:
        st.warning(f"Gagal mengambil data: {e}")
        return {}, pd.DataFrame()
