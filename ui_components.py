import streamlit as st
import pandas as pd

def display_fundamental_table(data):
    """Display fundamental data table with warning icons for missing data."""
    metrics = {
        "Price": data.get('price', 'N/A'),
        "Market Cap": data.get('market_cap', 'N/A'),
        "Volume": data.get('volume', 'N/A'),
        "PE Ratio": data.get('pe', 'N/A'),
        "PBV": data.get('pbv', 'N/A'),
        "EPS": data.get('eps', 'N/A'),
        "ROE": data.get('roe', 'N/A'),
        "Debt to Equity": data.get('debt_equity', 'N/A'),
        "Revenue Growth": data.get('revenue_growth', 'N/A'),
        "Net Profit Margin": data.get('net_margin', 'N/A')
    }
    df = pd.DataFrame(list(metrics.items()), columns=["Metrik", "Nilai"])
    df['Status'] = df['Nilai'].apply(lambda x: '⚠️' if x == 'N/A' else '')
    st.table(df)

def display_kpi_cards(data, indicators):
    """Display KPI cards with color-coded trends."""
    cols = st.columns(3)
    with cols[0]:
        st.metric("Harga Saat Ini", f"{data.get('price', 'N/A')}", delta=None)
    with cols[1]:
        trend = indicators['trend']
        arrow = "↑" if trend == 'Up' else "↓" if trend == 'Down' else "↔"
        color_class = "trend-arrow-up" if trend == 'Up' else "trend-arrow-down" if trend == 'Down' else "trend-arrow-side"
        st.markdown(f"<div class='kpi-card'>Arah Tren: <span class='{color_class}'>{arrow} {trend}</span></div>", unsafe_allow_html=True)
    with cols[2]:
        st.metric("RSI", f"{indicators['rsi']:.2f}" if indicators['rsi'] else 'N/A')

def display_score_gauge(final_score, f, t, r):
    """Display progress bars for scores."""
    cols = st.columns(4)
    with cols[0]:
        st.progress(final_score / 100)
        st.write(f"Skor Final: {final_score:.1f}")
    with cols[1]:
        st.progress(f / 100)
        st.write(f"Fundamental: {f:.1f}")
    with cols[2]:
        st.progress(t / 100)
        st.write(f"Teknikal: {t:.1f}")
    with cols[3]:
        st.progress(r / 100)
        st.write(f"Risiko: {r:.1f}")

def display_recommendation(decision, confidence, risk_level, horizon):
    """Display AI decision with color coding."""
    color = "green" if "BUY" in decision else "yellow" if decision == "HOLD" else "red"
    st.markdown(f"<h3 class='{color}'>Rekomendasi: {decision}</h3>", unsafe_allow_html=True)
    st.write(f"Tingkat Keyakinan: {confidence:.1f}%")
    st.write(f"Tingkat Risiko: {risk_level}")
    st.write(f"Horizon Waktu: {horizon}")

def display_explanation_panel(explanation):
    """Display expandable explanation panel."""
    with st.expander("Penjelasan AI (Transparan)"):
        st.write(explanation)

def display_conclusion(conclusion):
    """Display natural language conclusion."""
    st.subheader("Kesimpulan Analis")
    st.write(conclusion)
