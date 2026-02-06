def get_ai_decision(final_score, fundamental_score, technical_score, risk_score):
    """Simulate AI decision based on scores."""
    if final_score > 80:
        recommendation = "STRONG BUY"
    elif final_score > 60:
        recommendation = "BUY (Speculative)"
    elif final_score > 40:
        recommendation = "HOLD"
    else:
        recommendation = "AVOID"
    
    confidence = min(100, final_score + (100 - risk_score) / 2)  # Adjust based on risk
    risk_level = "Low" if risk_score > 70 else "Medium" if risk_score > 40 else "High"
    horizon = "Long-term" if fundamental_score > technical_score else "Short-term" if technical_score > fundamental_score else "Medium-term"
    
    return recommendation, confidence, risk_level, horizon

def get_ai_explanation(fundamental_score, technical_score, risk_score, data, indicators):
    """Generate readable explanation of AI reasoning."""
    explanation = []
    # Fundamental
    fund_help = []
    fund_hurt = []
    if 'pe' in data and data['pe']: fund_help.append(f"PE Ratio rendah ({data['pe']:.2f})" if data['pe'] < 15 else fund_hurt.append(f"PE Ratio tinggi ({data['pe']:.2f})"))
    if 'roe' in data and data['roe']: fund_help.append(f"ROE kuat ({data['roe']:.2f})") if data['roe'] > 0.15 else fund_hurt.append(f"ROE lemah ({data['roe']:.2f})"))
    explanation.append(f"Skor Fundamental ({fundamental_score:.1f}): Dibantu oleh {', '.join(fund_help) if fund_help else 'tidak ada'}. Dirugikan oleh {', '.join(fund_hurt) if fund_hurt else 'tidak ada'}.")
    
    # Technical
    tech_help = []
    tech_hurt = []
    if indicators['rsi'] < 30: tech_help.append("RSI oversold")
    elif indicators['rsi'] > 70: tech_hurt.append("RSI overbought")
    if indicators['trend'] == 'Up': tech_help.append("Tren naik yang kuat")
    explanation.append(f"Skor Teknikal ({technical_score:.1f}): Dibantu oleh {', '.join(tech_help) if tech_help else 'tidak ada'}. Dirugikan oleh {', '.join(tech_hurt) if tech_hurt else 'tidak ada'}.")
    
    # Risk
    risk_dom = "Volatilitas tinggi" if 'market_cap' in data and data['market_cap'] < 1e9 else "Likuiditas rendah"
    explanation.append(f"Skor Risiko ({risk_score:.1f}): Risiko dominan adalah {risk_dom}. Skor keseluruhan rendah karena ketidaklengkapan data atau volatilitas.")
    
    return "\n".join(explanation)

def get_ai_conclusion(data, indicators, recommendation, horizon):
    """Generate professional analyst-style natural language conclusion."""
    strengths = ["Valuasi menarik", "Pertumbuhan stabil"] if 'revenue_growth' in data and data['revenue_growth'] > 5 else ["Profitabilitas solid"]
    weaknesses = ["Utang tinggi"] if 'debt_equity' in data and data['debt_equity'] > 1.5 else ["Margin rendah"]
    risks = ["Volatilitas pasar", "Risiko sektor"]
    profile = "Investor konservatif" if recommendation in ["HOLD", "AVOID"] else "Investor agresif"
    short_outlook = "Potensi rebound jangka pendek jika tren volume meningkat." if indicators['volume_trend'] == 'Increasing' else "Hati-hati dengan tren sideways."
    long_outlook = "Prospek jangka panjang positif dengan ROE yang kuat." if 'roe' in data and data['roe'] > 0.1 else "Perlu monitor pertumbuhan revenue."
    
    conclusion = f"""
    Kekuatan: {', '.join(strengths)}.
    Kelemahan: {', '.join(weaknesses)}.
    Faktor Risiko: {', '.join(risks)}.
    Profil Investor yang Cocok: {profile}.
    Outlook Jangka Pendek: {short_outlook}
    Outlook Jangka Panjang: {long_outlook}
    """
    return conclusion
