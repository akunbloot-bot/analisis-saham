import streamlit as st
import time
from data_source import get_stock_data
from indicators import get_technical_indicators
from scoring import calculate_scores
from ai_analysis import get_ai_decision, get_ai_explanation, get_ai_conclusion
from ui_components import display_fundamental_table, display_kpi_cards, display_score_gauge, display_recommendation, display_explanation_panel, display_conclusion
from config import REFRESH_INTERVAL_OPTIONS, SCORING_THRESHOLDS

# Set page config for wide layout and title
st.set_page_config(layout="wide", page_title="Analisis Saham IDX")

# Custom CSS for fintech-grade UI: card-based, modern typography, subtle shadows
css = """
<style>
    .section { background-color: #f8f9fa; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .kpi-card { background-color: white; padding: 10px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stMetric { font-family: 'Arial', sans-serif; }
    .green { color: green; }
    .yellow { color: orange; }
    .red { color: red; }
    .trend-arrow-up { color: green; font-size: 1.5em; }
    .trend-arrow-down { color: red; font-size: 1.5em; }
    .trend-arrow-side { color: gray; font-size: 1.5em; }
</style>
"""
st.markdown(css, unsafe_allow_html=True)

# User input for ticker
ticker_input = st.text_input("Masukkan kode saham (contoh: BUMI, BBRI, TLKM)", value="", key="ticker").upper()
refresh_interval = st.selectbox("Interval auto-refresh (detik, 0 untuk mati)", REFRESH_INTERVAL_OPTIONS, index=0)

if ticker_input:
    symbol = ticker_input + ".JK"
    with st.spinner("Mengambil data saham..."):
        data, history = get_stock_data(symbol)
        if data and not history.empty:
            indicators = get_technical_indicators(history)
            fundamental_score, technical_score, risk_score, final_score, missing_penalty = calculate_scores(data, history, indicators)
            decision, confidence, risk_level, horizon = get_ai_decision(final_score, fundamental_score, technical_score, risk_score)
            explanation = get_ai_explanation(fundamental_score, technical_score, risk_score, data, indicators)
            conclusion = get_ai_conclusion(data, indicators, decision, horizon)

            # Display header
            st.header(f"Analisis Saham {ticker_input} ({symbol})")

            # Fundamental section
            st.subheader("Data Fundamental")
            col1, col2 = st.columns(2)
            with col1:
                display_fundamental_table(data)
            with col2:
                display_kpi_cards(data, indicators)

            # Technical section
            st.subheader("Analisis Teknikal")
            st.write(f"RSI (14): {indicators['rsi']:.2f}")
            st.write(f"MA20: {indicators['ma20']:.2f}, MA50: {indicators['ma50']:.2f}, MA200: {indicators['ma200']:.2f}")
            st.write(f"MACD: {indicators['macd']:.2f}, Signal: {indicators['signal']:.2f}")
            st.write(f"Tren Volume: {indicators['volume_trend']}")
            st.write(f"Arah Tren: {indicators['trend']}")

            # AI Scoring section
            st.subheader("Skor AI")
            display_score_gauge(final_score, fundamental_score, technical_score, risk_score)

            # AI Decision
            display_recommendation(decision, confidence, risk_level, horizon)

            # Explanation panel
            display_explanation_panel(explanation)

            # Conclusion
            display_conclusion(conclusion)
        else:
            st.error("Data tidak tersedia untuk saham ini. Coba ticker lain.")

    # Auto-refresh logic (non-blocking for short intervals, but sleeps UI)
    if refresh_interval > 0:
        time.sleep(refresh_interval)
        st.rerun()

