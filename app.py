import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from datetime import datetime
import yfinance as yf
from data_handler import fetch_stock_data
from stock_analyzer import analyze_stock, score_stock
import plotly.graph_objects as go

st.set_page_config(
    page_title="Analisis Saham Pribadi BEI", 
    page_icon="📈",
    layout="wide"
)

st.title("📈 Analisis Saham Pribadi BEI")
st.markdown("**Masukkan kode saham BEI** (contoh: BUMI, WEHA, BBRI, TLKM)")

# Sidebar untuk konfigurasi
st.sidebar.header("⚙️ Pengaturan")
period = st.sidebar.selectbox("Periode Grafik", ["6mo", "1y", "2y", "5y"], index=1)

# Input saham
col1, col2 = st.columns([3, 1])
with col1:
    symbol = st.text_input("Kode Saham:", placeholder="BUMI").upper().strip()
with col2:
    analyze_btn = st.button("🔍 Analisis", type="primary", use_container_width=True)

if analyze_btn and symbol:
    with st.spinner(f"📊 Mengambil data {symbol}.JK..."):
        data = fetch_stock_data(symbol, period)
    
    if data is None:
        st.error("❌ Gagal mengambil data. Pastikan kode saham benar!")
    else:
        analysis = analyze_stock(data)
        scoring = score_stock(analysis)
        
        # Header dengan nama saham
        st.header(f"**{data['nama_saham']} ({symbol})**")
        
        # Row 1: Metrics Primer
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💰 Harga Terkini", f"Rp {analysis['harga_terkini']:,}", delta=None)
        col2.metric("🏭 Market Cap", f"Rp {analysis['market_cap']:.1f}T")
        col3.metric("📊 PER", f"{analysis['per']:.2f}x")
        col4.metric("🔢 PBV", f"{analysis['pbv']:.2f}x")
        
        # Row 2: Metrics Sekunder
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("📈 EPS", f"Rp {analysis['eps']:,.0f}")
        col2.metric("💵 Laba Bersih", f"Rp {analysis['laba_bersih']:.1f}M")
        col3.metric("📉 Tren Laba", f"{analysis['tren_laba']*100:+.1f}%")
        col4.metric("🔄 Volume", f"{analysis['volume_rata']:,.0f}")
        
        # Kategori & Score (highlight)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"### 🎯 **{scoring['kategori']}**")
            st.metric("Total Score", f"{scoring['score']}/100", delta=None)
        with col2:
            st.markdown("### 💡 **Rekomendasi**")
            st.success(scoring['rekomendasi'])
        
        # Tabel Data Lengkap
        st.subheader("📋 Data Lengkap")
        df_metrics = pd.DataFrame({
            'Metrik': ['Harga Terkini', 'Market Cap', 'PER', 'PBV', 'EPS', 'Laba Bersih (TTM)', 
                      'Tren Laba (QoQ)', 'Volume Rata-rata', 'ROE Estimasi'],
            'Nilai': [
                f"Rp {analysis['harga_terkini']:,.0f}",
                f"Rp {analysis['market_cap']:.1f}T",
                f"{analysis['per']:.2f}x",
                f"{analysis['pbv']:.2f}x",
                f"Rp {analysis['eps']:,.0f}",
                f"Rp {analysis['laba_bersih']:.1f}M",
                f"{analysis['tren_laba']*100:.1f}%",
                f"{analysis['volume_rata']:,.0f} lembar",
                f"{analysis['roe']:.1f}%"
            ]
        })
        st.dataframe(df_metrics, use_container_width=True)
        
        # Grafik Harga & Volume
        st.subheader("📈 Grafik Harga & Volume")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['history'].index, y=data['history']['Close'], 
                                name='Harga Close', line=dict(color='blue', width=2)))
        fig.add_trace(go.Bar(x=data['history'].index, y=data['history']['Volume']/1e6, 
                            name='Volume (jt)', yaxis='y2', opacity=0.6))
        fig.update_layout(
            title=f"Harga & Volume {data['nama_saham']}",
            yaxis=dict(title="Harga (Rp)"),
            yaxis2=dict(title="Volume (jt lembar)", overlaying='y', side='right'),
            xaxis_title="Tanggal",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Detail Scoring (Transparan)
        st.subheader("⚖️ Detail Penilaian (Rule-based)")
        rules_df = pd.DataFrame(list(scoring['rules'].items()), columns=['Faktor', 'Skor'])
        st.dataframe(rules_df.style.highlight_max(axis=0, color='lightgreen'), 
                    use_container_width=True)
        st.info("**Rules mudah dimodifikasi di file `stock_analyzer.py`**")
        
        # Kesimpulan
        st.markdown("---")
        st.markdown("""
        ## 💡 **Kesimpulan Investasi**
        """)
        if scoring['score'] >= 70:
            st.success(f"✅ **{symbol} termasuk saham BAGUS!** Cocok untuk portofolio jangka {'panjang' if analysis['tren_laba'] > 0.1 else 'sedang'}.")
        elif scoring['score'] >= 40:
            st.warning(f"⚠️ **{symbol} SAHAM SEDANG.** Cocok untuk trading spekulatif.")
        else:
            st.error(f"❌ **{symbol} SAHAM BURUK.** Cari alternatif lain.")
        
        st.caption(f"Data diupdate: {datetime.now().strftime('%d/%m/%Y %H:%M WIB')} | Sumber: Yahoo Finance")

elif symbol:
    st.warning("Klik tombol **Analisis** untuk memulai!")

st.markdown("---")
st.markdown("**Disclaimer**: Analisis ini bersifat edukasi. Investasi saham berisiko tinggi. DYOR!")

