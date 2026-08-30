"""
Dashboard Business Intelligence — Segmentasi Pelanggan (RFM + K-Means)
Versi 8 (final) — konsep "Client Ledger": gading dominan, bingkai tinta hitam, aksen navy.
Tipografi Fraunces (display) + Inter (body) + IBM Plex Mono (data/ledger numerals).

Cara menjalankan:
    1. pip install streamlit pandas plotly
    2. streamlit run streamlit_app.py
Pastikan file 'rfm_segmentasi_pelanggan.csv' dan '.streamlit/config.toml' ada.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Client Ledger — Segmentasi Pelanggan",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Token warna ----------
IVORY = "#F7F4EC"        # dominan — gading hangat, bukan putih pucat
INK = "#12131A"          # bingkai — sidebar, header, garis tegas
CARD = "#FFFFFF"
NAVY = "#1C2B57"         # aksen utama
NAVY_DEEP = "#0F1938"
NAVY_SOFT = "#1C2B5712"
BORDER = "#12131A"
TEXT = "#1A1B22"
TEXT_MUTED = "#5C5E6B"

# Segmen: monokrom-navy bertingkat (gelap = paling bernilai) — kohesif, bukan warna acak
COLOR_MAP = {
    "Champions": "#0F1938",
    "Promising/New Active": "#2B4590",
    "At Risk": "#7D8CB8",
    "Lost/Churned": "#C3C9DC",
}
INITIAL_MAP = {"Champions": "C", "Promising/New Active": "P", "At Risk": "R", "Lost/Churned": "L"}
ORDER = ["Champions", "Promising/New Active", "At Risk", "Lost/Churned"]

INSIGHTS = {
    "Champions": "Pelanggan paling bernilai — baru bertransaksi, frekuensi tinggi, nilai belanja terbesar. "
                 "Diprioritaskan untuk program loyalitas dan akses awal produk baru.",
    "Promising/New Active": "Baru aktif dengan potensi berkembang. "
                             "Didorong lewat rekomendasi personal dan insentif transaksi kedua.",
    "At Risk": "Sebelumnya aktif, kini mulai jarang bertransaksi. "
               "Perlu kampanye keterlibatan ulang sebelum berpindah menjadi Lost.",
    "Lost/Churned": "Sudah lama tidak bertransaksi. "
                     "Kandidat kampanye win-back atau evaluasi ulang biaya retensi.",
}

# ---------- CSS ----------
st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    .stApp {{ background: {IVORY}; color: {TEXT}; }}
    * {{ font-family: 'Inter', sans-serif; }}

    section[data-testid="stSidebar"] {{ background: {INK}; }}
    section[data-testid="stSidebar"] * {{ color: #E7E5DC !important; }}
    section[data-testid="stSidebar"] .stCaption {{ color: #86899A !important; }}
    section[data-testid="stSidebar"] h3 {{
        font-family: 'IBM Plex Mono', monospace !important; font-size: 0.72rem !important;
        text-transform: uppercase; letter-spacing: 0.16em; color: #86899A !important; font-weight: 500 !important;
    }}

    h1, h2, h3, h4, h5 {{ font-family: 'Fraunces', serif !important; font-weight: 600 !important; color: {TEXT} !important; }}
    p, span, label, div {{ color: {TEXT}; }}
    .stCaption, [data-testid="stCaptionContainer"] p {{ color: {TEXT_MUTED} !important; }}

    /* ---- Masthead bergaya sertifikat/ledger nasabah ---- */
    .hero {{
        padding: 34px 40px; margin-bottom: 28px; background: {INK}; position: relative;
        border-bottom: 3px double {NAVY_SOFT.replace('12','')};
    }}
    .hero-top {{ display: flex; justify-content: space-between; align-items: flex-start; }}
    .crest {{
        width: 46px; height: 46px; border: 1.5px solid #9099B8; border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Fraunces', serif; font-size: 1.3rem; color: #C9CEE0; flex-shrink: 0;
    }}
    .hero .eyebrow {{
        font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; text-transform: uppercase;
        letter-spacing: 0.22em; color: #9099B8; margin-bottom: 10px;
    }}
    .hero h1 {{ font-size: 2.15rem; margin: 0 0 10px; letter-spacing: 0.005em; color: #F5F4EE !important; }}
    .hero p {{ color: #9A9CAE !important; margin: 0; font-size: 0.88rem; max-width: 520px; line-height: 1.6; }}
    .hero-meta {{
        text-align: right; font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem;
        color: #7A7D91; line-height: 1.8;
    }}
    .hero-meta b {{ color: #C9CEE0; }}

    /* ---- KPI: gaya nota/ledger, bukan kartu ala template ---- */
    .kpi-row {{ display: flex; border: 1px solid {BORDER}; background: {CARD}; }}
    .kpi-cell {{ flex: 1; padding: 18px 22px; border-right: 1px solid #E3E0D4; }}
    .kpi-cell:last-child {{ border-right: none; }}
    .kpi-label {{
        font-family: 'IBM Plex Mono', monospace; font-size: 0.64rem; text-transform: uppercase;
        letter-spacing: 0.1em; color: {TEXT_MUTED}; margin-bottom: 10px;
    }}
    .kpi-value {{
        font-family: 'IBM Plex Mono', monospace; font-size: 1.55rem; font-weight: 600; color: {NAVY_DEEP};
        font-variant-numeric: tabular-nums;
    }}

    /* ---- Panel umum ---- */
    .panel-title {{
        font-family: 'IBM Plex Mono', monospace; font-size: 0.68rem; text-transform: uppercase;
        letter-spacing: 0.12em; color: {TEXT_MUTED}; margin: 30px 0 14px; display: flex; align-items: center; gap: 10px;
    }}
    .panel-title::after {{ content: ""; flex: 1; height: 1px; background: #D8D4C4; }}

    .chart-frame {{ background: {CARD}; border: 1px solid {BORDER}; padding: 18px 20px; }}

    /* ---- Kartu segmen: badge medali + hairline, bukan blok warna tebal ---- */
    .seg-card {{
        display: flex; gap: 16px; padding: 18px 4px; border-bottom: 1px solid #DDD9CB;
    }}
    .seg-badge {{
        width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
        display: flex; align-items: center; justify-content: center;
        font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.05rem; color: #fff;
        background: var(--seg-color);
    }}
    .seg-card b {{ font-size: 1.1rem; font-family: 'Fraunces', serif; color: {TEXT}; }}
    .seg-card .desc {{ color: {TEXT_MUTED}; font-size: 0.85rem; margin-top: 4px; display: block; line-height: 1.55; }}

    div[data-testid="stMetric"] {{ background: {CARD}; padding: 10px; border: 1px solid {BORDER}; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 0; border-bottom: 1px solid {BORDER}; }}
    .stTabs [data-baseweb="tab"] {{
        color: {TEXT_MUTED}; background: transparent; font-family: 'IBM Plex Mono', monospace;
        font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em; padding: 0 18px 12px;
    }}
    .stTabs [aria-selected="true"] {{ color: {NAVY_DEEP} !important; border-bottom: 2px solid {NAVY_DEEP} !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: {NAVY_DEEP} !important; }}
    .stTabs [data-baseweb="tab-border"] {{ background-color: #DDD9CB !important; }}

    /* Tag filter: override paksa, termasuk inline style bawaan Streamlit */
    span[data-baseweb="tag"], div[data-baseweb="tag"],
    .stMultiSelect span[data-baseweb="tag"], .stMultiSelect div[data-baseweb="tag"] {{
        background-color: #1C1E29 !important; border: 1px solid #9099B8 !important; border-radius: 0 !important;
        color: #E7E5DC !important;
    }}
    span[data-baseweb="tag"] *, div[data-baseweb="tag"] * {{
        color: #E7E5DC !important; fill: #E7E5DC !important; background-color: transparent !important;
    }}

    div[data-baseweb="select"] > div {{
        background-color: #1C1E29 !important; border: 1px solid #3A3C4C !important; border-radius: 0 !important;
    }}
    div[data-baseweb="select"] > div:hover {{ border-color: #9099B8 !important; }}
    div[data-baseweb="popover"] ul {{ background-color: {INK} !important; border: 1px solid #3A3C4C !important; }}
    div[data-baseweb="popover"] li {{ color: #E7E5DC !important; }}
    div[data-baseweb="popover"] li:hover {{ background-color: #1C1E29 !important; }}

    section[data-testid="stSidebar"] input {{
        background-color: #1C1E29 !important; color: #E7E5DC !important; border: 1px solid #3A3C4C !important;
        border-radius: 0 !important;
    }}

    [data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; }}

    .stDownloadButton button {{
        background: transparent !important; color: #E7E5DC !important; border: 1px solid #9099B8 !important;
        border-radius: 0 !important; font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.74rem !important; letter-spacing: 0.06em; text-transform: uppercase;
    }}
    .stDownloadButton button:hover {{ background: #1C1E29 !important; border-color: #C9CEE0 !important; }}

    hr {{ border-color: #DDD9CB !important; }}
    ::-webkit-scrollbar {{ width: 8px; height: 8px; }}
    ::-webkit-scrollbar-thumb {{ background: {INK}; }}
</style>
""", unsafe_allow_html=True)

def base_layout(**overrides):
    layout = dict(
        paper_bgcolor=CARD, plot_bgcolor=CARD,
        font=dict(color=TEXT, family="Inter, sans-serif", size=12),
        xaxis=dict(gridcolor="#EDEAE0", zerolinecolor="#EDEAE0", color=TEXT_MUTED),
        yaxis=dict(gridcolor="#EDEAE0", zerolinecolor="#EDEAE0", color=TEXT_MUTED),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=TEXT_MUTED)),
        margin=dict(t=10, l=10, r=10, b=10),
    )
    layout.update(overrides)
    return layout


@st.cache_data
def load_data():
    return pd.read_csv("rfm_segmentasi_pelanggan.csv")

df = load_data()

# ---------- Sidebar ----------
st.sidebar.markdown("### Saring Data")
segments = st.sidebar.multiselect("Segmen Pelanggan", options=ORDER, default=ORDER)
cust_search = st.sidebar.text_input("Cari Customer ID")

filtered = df[df["Segmen"].isin(segments)]
if cust_search:
    filtered = filtered[filtered["CustomerID"].astype(str).str.contains(cust_search)]

st.sidebar.markdown("---")
st.sidebar.download_button(
    "↓  Unduh Data Terfilter",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="segmentasi_terfilter.csv",
    mime="text/csv",
    use_container_width=True,
)
st.sidebar.markdown("---")
st.sidebar.caption("Metode — RFM + K-Means (k=4)  \nSumber — Online Retail II  \nDiperbarui — otomatis dari data terkini")

# ---------- Hero (masthead) ----------
st.markdown("""
<div class="hero">
    <div class="hero-top">
        <div>
            <div class="eyebrow" style="color:#9099B8 !important">Client Ledger · Business Intelligence</div>
            <h1 style="color:#F7F5EF !important; -webkit-text-fill-color:#F7F5EF !important;">Segmentasi Nilai Pelanggan</h1>
            <p style="color:#B7B9C6 !important">Peta perilaku transaksi pelanggan e-commerce berdasarkan Recency, Frequency, dan
            Monetary — disusun untuk menjadi dasar strategi retensi dan akuisisi bernilai tinggi.</p>
        </div>
        <div class="crest">◆</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- KPI (gaya nota, satu baris tanpa jarak antar sel) ----------
st.markdown(f"""
<div class="kpi-row">
    <div class="kpi-cell"><div class="kpi-label">Total Pelanggan</div><div class="kpi-value">{len(filtered):,}</div></div>
    <div class="kpi-cell"><div class="kpi-label">Total Revenue</div><div class="kpi-value">£{filtered['Monetary'].sum():,.0f}</div></div>
    <div class="kpi-cell"><div class="kpi-label">Rata-rata Frequency</div><div class="kpi-value">{filtered['Frequency'].mean():.1f}×</div></div>
    <div class="kpi-cell"><div class="kpi-label">Rata-rata Recency</div><div class="kpi-value">{filtered['Recency'].mean():.0f} hari</div></div>
</div>
""", unsafe_allow_html=True)

# ---------- Summary ----------
summary = (
    filtered.groupby("Segmen")
    .agg(Jumlah=("CustomerID", "count"), Recency=("Recency", "mean"),
         Frequency=("Frequency", "mean"), Monetary=("Monetary", "mean"),
         TotalRevenue=("Monetary", "sum"))
    .round(1).reindex(ORDER).dropna(how="all").reset_index()
)
summary["Persentase"] = (summary["Jumlah"] / summary["Jumlah"].sum() * 100).round(1)

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["Ringkasan", "Detail Segmen", "Data Pelanggan"])

with tab1:
    st.markdown('<div class="panel-title">Sebaran Pelanggan — Recency × Monetary</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1.4, 1])

    with col_a:
        st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
        fig = px.scatter(
            filtered.sample(min(1500, len(filtered)), random_state=42) if len(filtered) > 0 else filtered,
            x="Recency", y="Monetary", color="Segmen", size="Frequency",
            color_discrete_map=COLOR_MAP, log_y=True, opacity=0.8,
            hover_data=["CustomerID"], category_orders={"Segmen": ORDER},
        )
        fig.update_traces(marker=dict(line=dict(width=0.5, color="#FFFFFF")))
        fig.update_layout(**base_layout(legend=dict(orientation="h", y=-0.22, bgcolor="rgba(0,0,0,0)")))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_b:
        st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
        fig_pie = px.pie(
            summary, names="Segmen", values="Jumlah", hole=0.66,
            color="Segmen", color_discrete_map=COLOR_MAP,
            category_orders={"Segmen": ORDER},
        )
        fig_pie.update_traces(textinfo="percent", textposition="outside",
                               marker=dict(line=dict(color=CARD, width=2)))
        fig_pie.update_layout(**base_layout(showlegend=True, legend=dict(orientation="v", font=dict(color=TEXT_MUTED))))
        st.plotly_chart(fig_pie, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">Kontribusi Revenue per Segmen</div>', unsafe_allow_html=True)
    st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
    fig2 = px.bar(
        summary.sort_values("TotalRevenue"), x="TotalRevenue", y="Segmen",
        orientation="h", color="Segmen", color_discrete_map=COLOR_MAP, text="TotalRevenue",
    )
    fig2.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
    fig2.update_layout(**base_layout(showlegend=False, yaxis_title="", xaxis_title="Total Revenue (£)"))
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="panel-title">Profil RFM Relatif per Segmen</div>', unsafe_allow_html=True)

    norm = summary.copy()
    for col in ["Recency", "Frequency", "Monetary"]:
        norm[col + "_n"] = (norm[col] - norm[col].min()) / (norm[col].max() - norm[col].min() + 1e-9)
    norm["Recency_score"] = 1 - norm["Recency_n"]

    st.markdown('<div class="chart-frame">', unsafe_allow_html=True)
    fig_radar = go.Figure()
    for _, row in norm.iterrows():
        c = COLOR_MAP.get(row["Segmen"], "#888")
        fig_radar.add_trace(go.Scatterpolar(
            r=[row["Recency_score"], row["Frequency_n"], row["Monetary_n"], row["Recency_score"]],
            theta=["Recency (semakin baru)", "Frequency", "Monetary", "Recency (semakin baru)"],
            fill="toself", name=row["Segmen"], line_color=c, fillcolor=c, opacity=0.22,
        ))
    fig_radar.update_layout(**base_layout(
        polar=dict(
            bgcolor=CARD,
            radialaxis=dict(visible=True, range=[0, 1], gridcolor="#EDEAE0", color=TEXT_MUTED),
            angularaxis=dict(gridcolor="#EDEAE0", color=TEXT_MUTED),
        ),
        showlegend=True,
    ))
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="panel-title">Rekomendasi Strategi per Segmen</div>', unsafe_allow_html=True)
    for seg in ORDER:
        if seg not in summary["Segmen"].values:
            continue
        color = COLOR_MAP[seg]
        st.markdown(f"""
            <div class="seg-card">
                <div class="seg-badge" style="--seg-color:{color}">{INITIAL_MAP[seg]}</div>
                <div>
                    <b>{seg}</b>
                    <span class="desc">{INSIGHTS[seg]}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="panel-title">Tabel Ringkasan Segmen</div>', unsafe_allow_html=True)
    st.dataframe(
        summary[["Segmen", "Jumlah", "Persentase", "Recency", "Frequency", "Monetary", "TotalRevenue"]],
        use_container_width=True, hide_index=True,
    )

with tab3:
    st.markdown(f'<div class="panel-title">Data Pelanggan — {len(filtered):,} baris</div>', unsafe_allow_html=True)
    st.dataframe(filtered, use_container_width=True, hide_index=True, height=520)
