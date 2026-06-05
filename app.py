"""
Interface Streamlit — Détection de Fraude Financière
Hackathon INTELO2026 — BYLL Ahlin (@bylljake)

Lancer : streamlit run app.py
"""

import uuid
import time
from pathlib import Path
from datetime import datetime, timezone

import streamlit as st

from fraud_detection import detect_fraud, load_transactions

SAMPLE_CSV = Path(__file__).parent / "data" / "sample_transactions.csv"

# ─────────────────────────────────────────────────────────────
# CSS GLOBAL — Dark Theme + Glassmorphism + Animations
# ─────────────────────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── RESET GLOBAL ── */
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

/* ── FOND ANIMÉ ── */
.stApp {
    background: linear-gradient(135deg, #0d0d1a 0%, #0a1628 40%, #0d1f2d 100%);
    background-attachment: fixed;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b2a 0%, #1a1a2e 100%) !important;
    border-right: 1px solid rgba(99,179,237,0.15);
}
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stRadio label { 
    color: #94a3b8 !important;
    transition: color 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { color: #63b3ed !important; }

/* ── HEADER HERO ── */
.hero-header {
    background: linear-gradient(135deg, rgba(99,179,237,0.1) 0%, rgba(236,72,153,0.08) 50%, rgba(167,139,250,0.1) 100%);
    border: 1px solid rgba(99,179,237,0.2);
    border-radius: 16px;
    padding: 28px 36px;
    margin-bottom: 28px;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at center, rgba(99,179,237,0.04) 0%, transparent 60%);
    animation: pulse-bg 6s ease-in-out infinite;
}
@keyframes pulse-bg {
    0%, 100% { transform: scale(1); opacity: 0.5; }
    50% { transform: scale(1.1); opacity: 1; }
}
.hero-title {
    font-size: 2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #a78bfa, #ec4899);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
}
.hero-subtitle {
    color: #94a3b8;
    font-size: 0.95rem;
    margin: 0;
    font-weight: 400;
}
.hero-badge {
    display: inline-block;
    background: rgba(99,179,237,0.15);
    border: 1px solid rgba(99,179,237,0.3);
    color: #63b3ed;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 3px 12px;
    border-radius: 20px;
    margin-bottom: 12px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── METRIC CARDS ── */
.kpi-grid { display: flex; gap: 16px; margin-bottom: 20px; }
.kpi-card {
    flex: 1;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 20px 24px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover {
    border-color: rgba(99,179,237,0.3);
    background: rgba(255,255,255,0.05);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(99,179,237,0.1);
}
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
}
.kpi-card.blue::after { background: linear-gradient(90deg, #63b3ed, #4299e1); }
.kpi-card.red::after { background: linear-gradient(90deg, #fc8181, #e53e3e); }
.kpi-card.purple::after { background: linear-gradient(90deg, #a78bfa, #7c3aed); }
.kpi-card.green::after { background: linear-gradient(90deg, #68d391, #38a169); }
.kpi-label {
    color: #718096;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 8px;
}
.kpi-value {
    font-size: 2.2rem;
    font-weight: 800;
    color: #f7fafc;
    line-height: 1;
    margin-bottom: 4px;
}
.kpi-sub {
    font-size: 0.8rem;
    color: #4a5568;
}
.kpi-icon { font-size: 1.5rem; float: right; margin-top: -4px; opacity: 0.6; }

/* ── ALERT BANNER ── */
.alert-fraud {
    background: linear-gradient(135deg, rgba(229,62,62,0.12), rgba(245,101,101,0.06));
    border: 1px solid rgba(229,62,62,0.4);
    border-left: 4px solid #e53e3e;
    border-radius: 10px;
    padding: 14px 20px;
    color: #feb2b2;
    font-weight: 500;
    margin: 16px 0;
    animation: slideIn 0.4s ease;
}
.alert-ok {
    background: linear-gradient(135deg, rgba(56,161,105,0.12), rgba(104,211,145,0.06));
    border: 1px solid rgba(56,161,105,0.4);
    border-left: 4px solid #38a169;
    border-radius: 10px;
    padding: 14px 20px;
    color: #9ae6b4;
    font-weight: 500;
    margin: 16px 0;
    animation: slideIn 0.4s ease;
}
@keyframes slideIn {
    from { opacity: 0; transform: translateX(-10px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ── GAUGE ── */
.gauge-wrap { text-align: center; padding: 10px; }
.gauge-title { color: #94a3b8; font-size: 0.8rem; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px; }
.gauge-value { font-size: 2.5rem; font-weight: 800; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.03);
    border-radius: 10px;
    padding: 4px;
    border: 1px solid rgba(255,255,255,0.07);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    color: #718096 !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 8px 20px !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,179,237,0.15) !important;
    color: #63b3ed !important;
}

/* ── FORM MANUEL ── */
.form-wrapper {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    backdrop-filter: blur(10px);
}
.form-title {
    color: #e2e8f0;
    font-size: 1.1rem;
    font-weight: 700;
    margin-bottom: 16px;
}

/* ── TABLE ── */
.stDataFrame { border-radius: 12px !important; border: 1px solid rgba(255,255,255,0.07) !important; }
[data-testid="stDataFrameResizable"] { background: rgba(255,255,255,0.02) !important; }

/* ── DIVIDER ── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── ALERT FEED ITEM ── */
.feed-item {
    display: flex;
    align-items: center;
    gap: 12px;
    background: rgba(229,62,62,0.07);
    border: 1px solid rgba(229,62,62,0.2);
    border-radius: 10px;
    padding: 12px 16px;
    margin-bottom: 8px;
    animation: fadeIn 0.3s ease;
}
.feed-item-ok {
    background: rgba(56,161,105,0.06);
    border-color: rgba(56,161,105,0.18);
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
}
.feed-dot { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.feed-dot-red { background: #e53e3e; box-shadow: 0 0 6px #e53e3e; }
.feed-dot-green { background: #38a169; box-shadow: 0 0 6px #38a169; }
.feed-info { flex: 1; }
.feed-id { color: #e2e8f0; font-weight: 600; font-size: 0.9rem; }
.feed-detail { color: #718096; font-size: 0.8rem; }
.feed-score { font-weight: 700; font-size: 1rem; }
.score-red { color: #fc8181; }
.score-green { color: #68d391; }

/* ── SECTION TITLE ── */
.section-title {
    color: #e2e8f0;
    font-size: 1.05rem;
    font-weight: 700;
    margin: 24px 0 12px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: rgba(255,255,255,0.08);
    margin-left: 8px;
}

/* ── SIDEBAR LOGO ── */
.sidebar-logo {
    text-align: center;
    padding: 8px 0 16px 0;
}
.sidebar-logo-text {
    font-size: 1.5rem;
    font-weight: 800;
    background: linear-gradient(135deg, #63b3ed, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.sidebar-logo-sub {
    color: #4a5568 !important;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── STBUTTON OVERRIDES ── */
.stButton > button {
    background: linear-gradient(135deg, #4299e1, #3182ce) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(66,153,225,0.4) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, rgba(99,179,237,0.1), rgba(99,179,237,0.05)) !important;
    color: #63b3ed !important;
    border: 1px solid rgba(99,179,237,0.3) !important;
    border-radius: 8px !important;
}

/* ── HIDE ALL STREAMLIT UI CHROME ── */
#MainMenu,
header[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
footer,
.viewerBadge_container__r5tak,
.styles_viewerBadge__CvC9N,
#stStreamlitRunOnSave,
.reportview-container .main footer,
[data-testid="manage-app-button"],
[data-testid="stChatInputAssistantButton"],
button[kind="ai"],
.stAiIcon,
[data-testid="stBottomBlockContainer"] button[aria-label*="AI"],
.st-emotion-cache-1wbqy5l,
iframe[title="streamlit_lottie.streamlit_lottie"],
.stDeployButton,
[data-testid="baseButton-header"],
[data-testid="stHeaderActionElements"] {
    display: none !important;
    visibility: hidden !important;
    height: 0 !important;
    position: fixed !important;
    z-index: -9999 !important;
}
header { height: 0 !important; min-height: 0 !important; }
.block-container { padding-top: 1.5rem !important; }

/* ── COUNTRY CARDS ── */
.country-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 14px;
    margin: 20px 0;
}
.country-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 18px 20px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
    position: relative;
    overflow: hidden;
}
.country-card:hover {
    border-color: rgba(167,139,250,0.4);
    background: rgba(255,255,255,0.06);
    transform: translateY(-3px);
    box-shadow: 0 8px 32px rgba(167,139,250,0.15);
}
.country-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #a78bfa, #ec4899);
    opacity: 0.7;
}
.country-flag {
    font-size: 2rem;
    margin-bottom: 6px;
}
.country-name {
    color: #e2e8f0;
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 10px;
}
.country-stat {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    border-top: 1px solid rgba(255,255,255,0.05);
}
.country-stat-label {
    color: #718096;
    font-size: 0.78rem;
    font-weight: 500;
}
.country-stat-value {
    color: #a78bfa;
    font-size: 0.85rem;
    font-weight: 700;
}
</style>
"""


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def risk_color(score: float) -> str:
    if score >= 0.75: return "#e53e3e"
    if score >= 0.5:  return "#ed8936"
    if score >= 0.25: return "#ecc94b"
    return "#38a169"

def risk_label(score: float) -> str:
    if score >= 0.75: return "CRITIQUE"
    if score >= 0.5:  return "ÉLEVÉ"
    if score >= 0.25: return "MODÉRÉ"
    return "FAIBLE"

def gauge_html(rate: float) -> str:
    color = risk_color(rate / 100)
    # SVG gauge arc
    pct = min(rate / 100, 1.0)
    angle = pct * 180
    # Convert to path
    import math
    r = 70
    cx, cy = 90, 90
    start_x = cx - r
    start_y = cy
    end_angle_rad = math.radians(180 - angle)
    end_x = cx + r * math.cos(end_angle_rad)
    end_y = cy - r * math.sin(end_angle_rad)
    large = 1 if angle > 180 else 0
    return f"""
    <div style="text-align:center; padding: 10px 0;">
        <svg width="180" height="110" viewBox="0 0 180 110">
            <!-- Track -->
            <path d="M {cx-r},{cy} A {r},{r} 0 0,1 {cx+r},{cy}"
                  fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="14" stroke-linecap="round"/>
            <!-- Fill -->
            <path d="M {cx-r},{cy} A {r},{r} 0 {large},1 {end_x:.2f},{end_y:.2f}"
                  fill="none" stroke="{color}" stroke-width="14" stroke-linecap="round"
                  style="filter: drop-shadow(0 0 6px {color});"/>
            <!-- Center text -->
            <text x="{cx}" y="{cy+4}" text-anchor="middle" font-size="22" font-weight="800" fill="{color}" font-family="Inter">{rate:.1f}%</text>
            <text x="{cx}" y="{cy+22}" text-anchor="middle" font-size="10" fill="#718096" font-family="Inter">TAUX DE FRAUDE</text>
        </svg>
    </div>
    """


# ─────────────────────────────────────────────────────────────
# RENDER INTERFACE
# ─────────────────────────────────────────────────────────────
def render_interface(transactions: list[dict], results: list[dict]) -> None:
    """
    Interface principale du tableau de bord de détection de fraude.
    Le jury évalue : clarté, utilité, intuitivité.
    """
    import pandas as pd
    import altair as alt
    import pydeck as pdk

    df_tx = pd.DataFrame(transactions)
    df_res = pd.DataFrame(results)
    df = pd.merge(df_tx, df_res, on="transaction_id")

    total_tx = len(df)
    suspicious_count = int(df["is_suspicious"].sum())
    legit_count = total_tx - suspicious_count
    fraud_rate = (suspicious_count / total_tx * 100) if total_tx > 0 else 0
    avg_score = float(df["fraud_score"].mean()) if total_tx > 0 else 0
    max_amount = float(df["amount"].dropna().max()) if total_tx > 0 else 0

    # Export CSV fraudes
    fraudulent_df = df[df["is_suspicious"] == True]
    csv_export = fraudulent_df.to_csv(index=False).encode("utf-8")

    # ── KPI CARDS ──────────────────────────────────────────────
    st.markdown(f"""
    <div class="kpi-grid">
        <div class="kpi-card blue">
            <div class="kpi-label">Transactions Analysées</div>
            <div class="kpi-value">{total_tx}</div>
            <div class="kpi-sub">Volume total analysé</div>
        </div>
        <div class="kpi-card red">
            <div class="kpi-label">Alertes Fraude</div>
            <div class="kpi-value" style="color:#fc8181;">{suspicious_count}</div>
            <div class="kpi-sub">Transactions bloquées</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-label">Légitimes</div>
            <div class="kpi-value" style="color:#68d391;">{legit_count}</div>
            <div class="kpi-sub">Transactions approuvées</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-label">Score Moyen de Risque</div>
            <div class="kpi-value" style="color:#a78bfa;">{avg_score:.2f}</div>
            <div class="kpi-sub">Sur une échelle de 0 à 1</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── ALERT / STATUS BANNER ─────────────────────────────────
    if suspicious_count > 0:
        st.markdown(f'<div class="alert-fraud"><strong>Action requise :</strong> {suspicious_count} transaction(s) ont franchi le seuil critique — investigation immédiate recommandée.</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="alert-ok"><strong>Système nominal :</strong> Toutes les transactions présentent un profil de risque acceptable.</div>', unsafe_allow_html=True)

    # ── MODE SIMULATION ──────────────────────────────────────
    col_sim, col_exp = st.columns([3, 1])
    with col_sim:
        mode_live = st.toggle("Mode Simulation Temps Réel", value=False, help="Rejoue l'arrivée des transactions en direct")
    with col_exp:
        if not fraudulent_df.empty:
            st.download_button("Rapport CSV", data=csv_export, file_name="rapport_fraudes_intelo2026.csv", mime="text/csv", use_container_width=True)

    if mode_live:
        st.info("Simulation démarrée — les transactions arrivent en temps réel...")
        ph = st.empty()
        for i in range(1, len(df) + 1):
            cur = df.head(i)
            last = cur.iloc[-1]
            if last["is_suspicious"]:
                st.toast(f"Fraude : {last.get('amount', '?')}€ | {last.get('merchant', '?')} | {last.get('country', '?')}")
            with ph.container():
                c1, c2, c3 = st.columns(3)
                c1.metric("Traitées", i, delta=None)
                c2.metric("Fraudes", int(cur["is_suspicious"].sum()))
                c3.metric("Taux", f"{(cur['is_suspicious'].sum()/i*100):.1f}%")
                st.dataframe(
                    cur[["transaction_id", "user_id", "amount", "fraud_score", "is_suspicious", "reason"]].tail(5),
                    use_container_width=True, hide_index=True
                )
            time.sleep(st.session_state.get("sim_speed", 0.3))
        st.success("Simulation terminée.")
        return

    # ── COORDS PAYS ──────────────────────────────────────────
    COORDS = {
        "FR": [2.21, 46.23], "US": [-95.71, 37.09], "GB": [-3.44, 55.38],
        "DE": [10.45, 51.17], "IT": [12.57, 41.87], "ES": [-3.75, 40.46],
        "CN": [104.20, 35.86], "JP": [138.25, 36.20], "BR": [-51.93, -14.24],
        "RU": [105.32, 61.52], "IN": [78.96, 20.59], "CA": [-106.35, 56.13],
        "AU": [133.78, -25.27], "ZA": [22.94, -30.56], "MX": [-102.55, 23.63],
        "NG": [8.68, 9.08],
    }

    # ── TABS ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Analyse Visuelle", "Carte 3D", "Clients par Pays", "Rapport", "Alertes en direct"])

    # ─── TAB 1 : Graphiques ──────────────────────────────────
    with tab1:
        col_g1, col_g2, col_g3 = st.columns([2, 1, 1])

        with col_g1:
            st.markdown('<div class="section-title">Distribution des Scores de Risque</div>', unsafe_allow_html=True)
            chart = alt.Chart(df).mark_bar(
                opacity=0.85, cornerRadiusTopLeft=4, cornerRadiusTopRight=4
            ).encode(
                x=alt.X("fraud_score:Q", bin=alt.Bin(maxbins=20), title="Score de risque", axis=alt.Axis(grid=False, labelColor="#718096", titleColor="#718096")),
                y=alt.Y("count()", title="Volume", axis=alt.Axis(grid=True, gridColor="rgba(255,255,255,0.04)", labelColor="#718096", titleColor="#718096")),
                color=alt.condition(
                    alt.datum.fraud_score >= 0.5,
                    alt.value("#e53e3e"),
                    alt.value("#4299e1")
                ),
                tooltip=["count()", alt.Tooltip("fraud_score:Q", format=".2f")]
            ).properties(height=300, background="transparent").configure_view(strokeWidth=0)
            st.altair_chart(chart, use_container_width=True)

        with col_g2:
            st.markdown('<div class="section-title">Répartition</div>', unsafe_allow_html=True)
            pie = alt.Chart(df).mark_arc(innerRadius=55, outerRadius=90, cornerRadius=4).encode(
                theta=alt.Theta(field="is_suspicious", type="nominal", aggregate="count"),
                color=alt.Color("is_suspicious:N",
                    scale=alt.Scale(domain=[False, True], range=["#4299e1", "#e53e3e"]),
                    legend=alt.Legend(title=None, orient="bottom", labelColor="#94a3b8", labelFontSize=11)
                ),
                tooltip=["is_suspicious", "count()"]
            ).properties(height=280, background="transparent").configure_view(strokeWidth=0)
            st.altair_chart(pie, use_container_width=True)

        with col_g3:
            st.markdown('<div class="section-title">Jauge de Risque</div>', unsafe_allow_html=True)
            st.markdown(gauge_html(fraud_rate), unsafe_allow_html=True)
            color = risk_color(fraud_rate / 100)
            label = risk_label(fraud_rate / 100)
            st.markdown(f'<div style="text-align:center;margin-top:-8px;"><span style="background:rgba(229,62,62,0.12);border:1px solid {color};color:{color};padding:3px 14px;border-radius:20px;font-size:0.8rem;font-weight:700;letter-spacing:1px;">{label}</span></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Montants par Transaction</div>', unsafe_allow_html=True)
        line = alt.Chart(df.reset_index()).mark_area(
            line={"color": "#63b3ed", "strokeWidth": 2},
            color=alt.Gradient(
                gradient="linear",
                stops=[alt.GradientStop(color="rgba(99,179,237,0.3)", offset=0),
                       alt.GradientStop(color="rgba(99,179,237,0.0)", offset=1)],
                x1=1, x2=1, y1=1, y2=0
            ),
            point=alt.OverlayMarkDef(color="white", size=50)
        ).encode(
            x=alt.X("index:Q", title="N° Transaction", axis=alt.Axis(labelColor="#718096", titleColor="#718096", grid=False)),
            y=alt.Y("amount:Q", title="Montant (€)", axis=alt.Axis(labelColor="#718096", titleColor="#718096", gridColor="rgba(255,255,255,0.04)")),
            color=alt.condition(
                alt.datum.is_suspicious == True,
                alt.value("#e53e3e"),
                alt.value("#63b3ed")
            ),
            tooltip=["transaction_id", "user_id", alt.Tooltip("amount:Q", format=".2f"), "is_suspicious", "reason"]
        ).properties(height=220, background="transparent").configure_view(strokeWidth=0)
        st.altair_chart(line, use_container_width=True)

    # ─── TAB 2 : Carte 3D ────────────────────────────────────
    with tab2:
        st.markdown('<div class="section-title">Carte Géographique 3D des Risques</div>', unsafe_allow_html=True)
        st.caption("Maintenez **Shift + clic gauche** pour incliner la caméra. Les colonnes **rouges** signalent des fraudes détectées.")


        import plotly.express as px
        import plotly.graph_objects as go
        
        df_map = df.copy()
        df_map["lon"] = df_map["country"].apply(lambda c: COORDS.get(c, [0, 0])[0] if isinstance(c, str) else 0)
        df_map["lat"] = df_map["country"].apply(lambda c: COORDS.get(c, [0, 0])[1] if isinstance(c, str) else 0)
        geo = df_map.groupby(["country", "lon", "lat"]).agg(
            total=("transaction_id", "count"),
            fraudes=("is_suspicious", "sum"),
            montant_total=("amount", "sum")
        ).reset_index()
        
        fig = px.scatter_geo(
            geo,
            lon="lon",
            lat="lat",
            size="total",
            color="fraudes",
            hover_name="country",
            hover_data={"lon": False, "lat": False, "total": True, "fraudes": True, "montant_total": True},
            projection="orthographic",
            color_continuous_scale=["#4299e1", "#e53e3e"],
            title="Globe 3D des Transactions et Fraudes"
        )
        
        fig.update_geos(
            showcountries=True, countrycolor="rgba(255, 255, 255, 0.2)",
            showcoastlines=True, coastlinecolor="rgba(255, 255, 255, 0.2)",
            showland=True, landcolor="rgba(255, 255, 255, 0.05)",
            showocean=True, oceancolor="rgba(10, 22, 40, 0.8)",
            bgcolor="rgba(0,0,0,0)",
            resolution=50
        )
        
        fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            geo=dict(bgcolor="rgba(0,0,0,0)"),
            font=dict(color="#e2e8f0")
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # Top pays à risque
        if not geo.empty:
            st.markdown('<div class="section-title">Top Pays à Risque</div>', unsafe_allow_html=True)
            top_risk = geo[geo["fraudes"] > 0].sort_values("fraudes", ascending=False).head(5)
            if not top_risk.empty:
                bar_risk = alt.Chart(top_risk).mark_bar(cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
                    x=alt.X("country:N", title=None, axis=alt.Axis(labelColor="#718096")),
                    y=alt.Y("fraudes:Q", title="Nb Fraudes", axis=alt.Axis(labelColor="#718096", gridColor="rgba(255,255,255,0.04)")),
                    color=alt.value("#e53e3e"),
                    tooltip=["country", "fraudes", "total"]
                ).properties(height=200, background="transparent").configure_view(strokeWidth=0)
                st.altair_chart(bar_risk, use_container_width=True)
            else:
                st.info("Aucun pays suspect dans les données.")

    # ─── TAB 3 : Clients par Pays (Carte) ─────────────────────
    with tab3:
        st.markdown('<div class="section-title">Répartition des Clients par Pays</div>', unsafe_allow_html=True)
        st.caption("Nombre de **clients uniques** par pays. Survolez les pays sur la carte pour voir les détails.")

        COUNTRY_NAMES = {
            "FR": "France", "US": "États-Unis", "GB": "Royaume-Uni",
            "DE": "Allemagne", "IT": "Italie", "ES": "Espagne",
            "CN": "Chine", "JP": "Japon", "BR": "Brésil",
            "RU": "Russie", "IN": "Inde", "CA": "Canada",
            "AU": "Australie", "ZA": "Afrique du Sud", "MX": "Mexique",
            "NG": "Nigéria",
        }

        df_clients = df.copy()
        df_clients["longitude"] = df_clients["country"].apply(lambda c: COORDS.get(c, [0, 0])[0] if isinstance(c, str) else 0)
        df_clients["latitude"] = df_clients["country"].apply(lambda c: COORDS.get(c, [0, 0])[1] if isinstance(c, str) else 0)

        clients_by_country = df_clients.groupby(["country", "longitude", "latitude"]).agg(
            nb_clients=("user_id", "nunique"),
            nb_transactions=("transaction_id", "count"),
            montant_total=("amount", "sum")
        ).reset_index()
        clients_by_country["country_name"] = clients_by_country["country"].map(COUNTRY_NAMES).fillna(clients_by_country["country"])

        # Carte interactive Plotly
        if not clients_by_country.empty:
            import plotly.express as px
            fig = px.scatter_geo(
                clients_by_country,
                lon="longitude",
                lat="latitude",
                size="nb_clients",
                color="nb_clients",
                hover_name="country_name",
                hover_data={"longitude": False, "latitude": False, "nb_clients": True, "nb_transactions": True, "montant_total": True},
                projection="orthographic",
                color_continuous_scale=px.colors.sequential.Purp,
            )
            fig.update_geos(
                showcountries=True, countrycolor="rgba(255, 255, 255, 0.2)",
                showcoastlines=True, coastlinecolor="rgba(255, 255, 255, 0.2)",
                showland=True, landcolor="rgba(255, 255, 255, 0.05)",
                showocean=True, oceancolor="rgba(10, 22, 40, 0.8)",
                bgcolor="rgba(0,0,0,0)"
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                geo=dict(bgcolor="rgba(0,0,0,0)")
            )
            st.plotly_chart(fig, use_container_width=True)

        # Cartes pays stylées
        if not clients_by_country.empty:
            st.markdown('<div class="section-title">Détails par Pays</div>', unsafe_allow_html=True)
            sorted_countries = clients_by_country.sort_values("nb_clients", ascending=False)
            cards_html = '<div class="country-grid">'
            for _, row in sorted_countries.iterrows():
                code = row["country"] if isinstance(row["country"], str) else "??"
                name = row["country_name"]
                clients = int(row["nb_clients"])
                txs = int(row["nb_transactions"])
                volume = row["montant_total"]
                cards_html += f'''
                <div class="country-card">
                    <div class="country-name">{name}</div>
                    <div class="country-stat">
                        <span class="country-stat-label">Clients uniques</span>
                        <span class="country-stat-value">{clients}</span>
                    </div>
                    <div class="country-stat">
                        <span class="country-stat-label">Transactions</span>
                        <span class="country-stat-value">{txs}</span>
                    </div>
                    <div class="country-stat">
                        <span class="country-stat-label">Volume total</span>
                        <span class="country-stat-value">{volume:,.0f} €</span>
                    </div>
                </div>
                '''
            cards_html += '</div>'
            st.markdown(cards_html, unsafe_allow_html=True)

            # Bar chart clients par pays
            display_clients = clients_by_country[["country_name", "country", "nb_clients", "nb_transactions", "montant_total"]].sort_values("nb_clients", ascending=False)
            bar_clients = alt.Chart(display_clients).mark_bar(
                cornerRadiusTopLeft=4, cornerRadiusTopRight=4
            ).encode(
                x=alt.X("country_name:N", title=None, sort="-y", axis=alt.Axis(labelColor="#718096", labelAngle=-45)),
                y=alt.Y("nb_clients:Q", title="Clients Uniques", axis=alt.Axis(labelColor="#718096", gridColor="rgba(255,255,255,0.04)")),
                color=alt.value("#a78bfa"),
                tooltip=["country_name", "nb_clients", "nb_transactions"]
            ).properties(height=250, background="transparent").configure_view(strokeWidth=0)
            st.altair_chart(bar_clients, use_container_width=True)

    # ─── TAB 4 : Rapport Détaillé ────────────────────────────
    with tab4:
        col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
        with col_f1:
            filter_mode = st.selectbox("Filtrer par", ["Toutes", "Suspectes uniquement", "Légitimes uniquement"])
        with col_f2:
            sort_col = st.selectbox("Trier par", ["fraud_score", "amount", "transaction_id"])
        with col_f3:
            sort_asc = st.toggle("Ordre croissant", value=False)

        df_disp = df.copy()
        if filter_mode == "Suspectes uniquement":
            df_disp = df_disp[df_disp["is_suspicious"] == True]
        elif filter_mode == "Légitimes uniquement":
            df_disp = df_disp[df_disp["is_suspicious"] == False]
        df_disp = df_disp.sort_values(sort_col, ascending=sort_asc)

        st.dataframe(
            df_disp[["transaction_id", "user_id", "amount", "currency", "merchant", "country", "card_present", "fraud_score", "reason"]],
            use_container_width=True, hide_index=True,
            column_config={
                "transaction_id": "ID",
                "user_id": "Client",
                "amount": st.column_config.NumberColumn("Montant", format="%.2f €"),
                "currency": "Devise",
                "merchant": "Marchand",
                "country": "Pays",
                "card_present": st.column_config.CheckboxColumn("Carte présente"),
                "fraud_score": st.column_config.ProgressColumn("Score Risque", format="%.2f", min_value=0, max_value=1),
                "reason": "Diagnostic IA",
            }
        )
        st.caption(f"{len(df_disp)} résultats affichés sur {total_tx} transactions analysées.")

    # ─── TAB 5 : Flux d'Alertes ──────────────────────────────
    with tab5:
        st.markdown('<div class="section-title">Flux des Alertes en Temps Réel</div>', unsafe_allow_html=True)
        st.caption("Toutes les transactions analysées, classées par score de risque décroissant.")
        df_feed = df.sort_values("fraud_score", ascending=False)
        for _, row in df_feed.iterrows():
            is_sus = row["is_suspicious"]
            dot_class = "feed-dot-red" if is_sus else "feed-dot-green"
            item_class = "feed-item" if is_sus else "feed-item feed-item-ok"
            score_class = "score-red" if is_sus else "score-green"
            flag = "" if is_sus else ""
            st.markdown(f"""
            <div class="{item_class}">
                <div class="feed-dot {dot_class}"></div>
                <div class="feed-info">
                    <div class="feed-id">{row["transaction_id"]} — {row.get("merchant","?")}</div>
                    <div class="feed-detail">Client : {row.get("user_id","?")} · {row.get("amount","?")} € · {row.get("country","?")} · {row.get("reason","")}</div>
                </div>
                <div class="feed-score {score_class}">{row["fraud_score"]:.2f}</div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────
def main() -> None:
    st.set_page_config(
        page_title="FraudShield — Détection IA · INTELO2026",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Injection CSS global
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    # ── SIDEBAR ─────────────────────────────────────────────
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-logo">
            <div class="sidebar-logo-text">FraudShield</div>
            <div class="sidebar-logo-sub">by BYLL Ahlin · INTELO2026</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()

        st.markdown("**Source de Données**")
        data_source = st.radio("", ["Exemple fourni", "Import CSV", "Saisie manuelle"], label_visibility="collapsed")

        if "manual_txs" not in st.session_state:
            st.session_state["manual_txs"] = []

        transactions: list[dict] = []

        if data_source == "Exemple fourni":
            transactions = load_transactions(str(SAMPLE_CSV))
            st.success(f"{len(transactions)} transactions chargées")

        elif data_source == "Import CSV":
            uploaded = st.file_uploader("Fichier CSV", type=["csv"])
            if uploaded:
                tmp = Path(".streamlit_upload.csv")
                tmp.write_bytes(uploaded.getvalue())
                transactions = load_transactions(str(tmp))
                tmp.unlink(missing_ok=True)
                st.success(f"{len(transactions)} transactions importées")
            else:
                st.info("Déposez un fichier CSV ci-dessus.")

        elif data_source == "Saisie manuelle":
            transactions = st.session_state["manual_txs"]
            if transactions:
                st.success(f"{len(transactions)} transaction(s) en mémoire")
                if st.button("Réinitialiser", use_container_width=True):
                    st.session_state["manual_txs"] = []
                    st.rerun()

        st.divider()
        st.markdown("**Paramètres de Simulation**")
        sim_speed = st.slider("Vitesse (s/transaction)", 0.05, 2.0, 0.3, 0.05)
        st.session_state["sim_speed"] = sim_speed

        st.divider()
        st.markdown("""
        <div style="color:#4a5568;font-size:0.75rem;line-height:1.6;">
        <strong style="color:#718096;">Astuce Jury :</strong><br>
        Activez le <em>Mode Simulation</em> pour voir le système analyser les transactions en direct.<br><br>
        <span style="color:#e53e3e;">●</span> Fraude détectée<br>
        <span style="color:#4299e1;">●</span> Transaction légitime
        </div>
        """, unsafe_allow_html=True)

    # ── HERO HEADER ─────────────────────────────────────────
    st.markdown("""
    <div class="hero-header">
        <div class="hero-badge">Hackathon INTELO2026</div>
        <div class="hero-title">FraudShield — Détection de Fraude</div>
        <p class="hero-subtitle">Plateforme temps-réel de détection et d'analyse des fraudes financières · BYLL Ahlin</p>
    </div>
    """, unsafe_allow_html=True)

    # ── FORMULAIRE MANUEL (dans la page principale) ─────────
    if data_source == "Saisie manuelle":
        st.markdown('<div class="section-title">Nouvelle Transaction</div>', unsafe_allow_html=True)
        with st.form("tx_form", clear_on_submit=True, border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c1:
                user_id = st.text_input("Client (ID)", value="U-001", placeholder="U-001")
                merchant = st.text_input("Marchand", value="Amazon", placeholder="Amazon")
            with c2:
                amount = st.number_input("Montant (€)", min_value=-9999.0, max_value=999999.0, value=50.0, step=10.0)
                country = st.selectbox("Pays", ["FR", "US", "GB", "DE", "IT", "ES", "CN", "JP", "BR", "RU", "IN", "CA", "AU", "ZA", "MX", "NG"])
            with c3:
                card_present = st.checkbox("Carte Physique", value=True)
                st.write("")
            with c4:
                st.write("")
                submitted = st.form_submit_button("Ajouter & Analyser", use_container_width=True, type="primary")

            if submitted:
                tx = {
                    "transaction_id": f"TX-{str(uuid.uuid4())[:8].upper()}",
                    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "user_id": user_id,
                    "amount": float(amount),
                    "currency": "EUR",
                    "merchant": merchant,
                    "country": country,
                    "card_present": card_present,
                }
                st.session_state["manual_txs"].append(tx)
                transactions = st.session_state["manual_txs"]
                st.toast(f"Transaction {tx['transaction_id']} ajoutée !")
                st.rerun()

        st.divider()

    # ── GUARDS ───────────────────────────────────────────────
    if not transactions:
        if data_source == "Saisie manuelle":
            st.markdown('<div style="text-align:center;padding:60px 0;color:#4a5568;font-size:1.1rem;">Entrez votre première transaction ci-dessus pour démarrer l\'analyse.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div style="text-align:center;padding:60px 0;color:#4a5568;font-size:1.1rem;">Choisissez une source de données dans le panneau de gauche.</div>', unsafe_allow_html=True)
        return

    # ── ANALYSE ──────────────────────────────────────────────
    with st.spinner("Analyse en cours..."):
        try:
            results = detect_fraud(transactions)
        except NotImplementedError:
            st.error("Implémentez d'abord `detect_fraud` dans `fraud_detection.py`.")
            return
        except Exception as exc:
            st.error(f"Erreur : {exc}")
            return

    render_interface(transactions, results)


if __name__ == "__main__":
    main()
