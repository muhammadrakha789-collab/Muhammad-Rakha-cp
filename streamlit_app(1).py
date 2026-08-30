"""
Dashboard Business Intelligence — Segmentasi Pelanggan (RFM + K-Means)
Cara menjalankan:
    1. pip install streamlit pandas plotly
    2. streamlit run streamlit_app.py
Pastikan file 'rfm_segmentasi_pelanggan.csv' berada di folder yang sama.
"""
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard Segmentasi Pelanggan", page_icon="📊", layout="wide", initial_sidebar_state="expanded")

COLOR_MAP = {
    "Champions": "#D4AF37",
    "Promising/New Active": "#3FAF9F",
    "At Risk": "#E58A2B",
    "Lost/Churned": "#D45B61",
}

st.markdown("""
<style>
.stApp { background:#0B0B0B; color:#F5F5F5; }
section[data-testid="stSidebar"] { background:#080808; border-right:1px solid #242424; }
section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] p { color:#F2F2F2 !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] > div { background:#111 !important; border:1px solid #343434 !important; border-radius:10px !important; }
section[data-testid="stSidebar"] div[data-baseweb="select"] span { color:#F4F4F4 !important; }
div[data-baseweb="popover"], div[role="option"] { background:#111 !important; color:#F4F4F4 !important; }
div[role="option"]:hover { background:#222 !important; }
h1 { font-weight:750 !important; letter-spacing:-.5px; }
h2,h3 { font-weight:650 !important; }
div[data-testid="stMetric"] { background:#111; border:1px solid #292929; border-radius:14px; padding:18px 20px; min-height:118px; box-shadow:0 6px 18px rgba(0,0,0,.18); }
div[data-testid="stMetricLabel"] { color:#AFAFAF !important; font-size:.88rem !important; }
div[data-testid="stMetricValue"] { color:#FFF !important; font-weight:750 !important; }
div[data-testid="stTabs"] button { color:#BDBDBD; }
div[data-testid="stTabs"] button[aria-selected="true"] { color:#FFF; }
.stButton > button { width:100%; border-radius:9px; border:1px solid #343434; background:#151515; color:#FFF; }
.stButton > button:hover { border-color:#666; background:#202020; color:#FFF; }
.info-card { background:#111; border:1px solid #292929; border-radius:13px; padding:16px 18px; margin:8px 0 16px; }
.info-title { font-size:1rem; font-weight:700; margin-bottom:5px; color:#FFF; }
.info-text { color:#AFAFAF; font-size:.88rem; line-height:1.55; }
.footer { text-align:center; color:#777; font-size:.78rem; padding:25px 0 10px; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    return pd.read_csv("rfm_segmentasi_pelanggan.csv")

df = load_data()
required = {"CustomerID", "Segmen", "Recency", "Frequency", "Monetary"}
missing = required - set(df.columns)
if missing:
    st.error("Kolom berikut belum tersedia pada dataset: " + ", ".join(sorted(missing)))
    st.stop()

st.title("📊 Dashboard Segmentasi Pelanggan E-Commerce")
st.caption("Analisis pelanggan menggunakan RFM (Recency, Frequency, Monetary) + K-Means Clustering")
st.markdown("""
<div class="info-card"><div class="info-title">💡 Cara membaca dashboard</div>
<div class="info-text">Gunakan filter di sebelah kiri untuk memilih segmen pelanggan. Kartu KPI menunjukkan kondisi pelanggan yang dipilih, sedangkan grafik membantu melihat pola perilaku dan kontribusi revenue.</div></div>
""", unsafe_allow_html=True)

# FILTER HITAM
st.sidebar.markdown("## 🎛️ Filter Dashboard")
st.sidebar.caption("Gunakan filter untuk memfokuskan analisis.")
all_segments = sorted(df["Segmen"].dropna().unique().tolist())
b1,b2 = st.sidebar.columns(2)
with b1:
    if st.button("Pilih Semua"): st.session_state["selected_segments"] = all_segments
with b2:
    if st.button("Kosongkan"): st.session_state["selected_segments"] = []
if "selected_segments" not in st.session_state: st.session_state["selected_segments"] = all_segments
segments = st.sidebar.multiselect("Pilih Segmen", options=all_segments, key="selected_segments")
search_customer = st.sidebar.text_input("🔎 Cari Customer ID", placeholder="Contoh: 12345")
filtered = df[df["Segmen"].isin(segments)].copy()
if search_customer.strip():
    filtered = filtered[filtered["CustomerID"].astype(str).str.lower().str.contains(search_customer.strip().lower(), na=False)]
st.sidebar.divider()
st.sidebar.caption(f"Menampilkan **{len(filtered):,}** pelanggan dari **{len(df):,}** data.")
if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan filter. Silakan pilih minimal satu segmen.")
    st.stop()

# KPI
col1,col2,col3,col4 = st.columns(4)
col1.metric("👥 Total Pelanggan", f"{len(filtered):,}")
col2.metric("💷 Total Revenue", f"£{filtered['Monetary'].sum():,.0f}")
col3.metric("🔁 Rata-rata Frequency", f"{filtered['Frequency'].mean():.1f}x")
col4.metric("⏱️ Rata-rata Recency", f"{filtered['Recency'].mean():.0f} hari")
st.divider()

summary=(filtered.groupby("Segmen").agg(Jumlah=("CustomerID","count"),Recency=("Recency","mean"),Frequency=("Frequency","mean"),Monetary=("Monetary","mean"),TotalRevenue=("Monetary","sum")).round(1).reset_index())
summary["Persentase"]=(summary["Jumlah"]/summary["Jumlah"].sum()*100).round(1)

col_a,col_b=st.columns([1.3,1])
with col_a:
    st.subheader("Sebaran Pelanggan")
    st.caption("Recency vs Monetary — ukuran titik menunjukkan Frequency.")
    sample=filtered.sample(min(1500,len(filtered)),random_state=42)
    fig=px.scatter(sample,x="Recency",y="Monetary",color="Segmen",size="Frequency",color_discrete_map=COLOR_MAP,log_y=True,opacity=.68,hover_data=["CustomerID"],template="plotly_dark")
    fig.update_layout(paper_bgcolor="#0B0B0B",plot_bgcolor="#0B0B0B",font=dict(color="#EAEAEA"),margin=dict(l=10,r=10,t=20,b=10),legend_title_text="Segmen")
    fig.update_xaxes(gridcolor="#242424",zerolinecolor="#242424"); fig.update_yaxes(gridcolor="#242424",zerolinecolor="#242424")
    st.plotly_chart(fig,use_container_width=True)
with col_b:
    st.subheader("Kontribusi Revenue")
    st.caption("Total revenue berdasarkan segmen pelanggan.")
    fig2=px.bar(summary.sort_values("TotalRevenue"),x="TotalRevenue",y="Segmen",orientation="h",color="Segmen",color_discrete_map=COLOR_MAP,text="TotalRevenue",template="plotly_dark")
    fig2.update_traces(texttemplate="£%{text:,.0f}",textposition="outside",cliponaxis=False)
    fig2.update_layout(showlegend=False,paper_bgcolor="#0B0B0B",plot_bgcolor="#0B0B0B",font=dict(color="#EAEAEA"),margin=dict(l=10,r=55,t=20,b=10))
    fig2.update_xaxes(gridcolor="#242424"); fig2.update_yaxes(gridcolor="#242424")
    st.plotly_chart(fig2,use_container_width=True)

st.subheader("📈 Analisis Komposisi Pelanggan")
tab1,tab2,tab3=st.tabs(["Komposisi Segmen","Perbandingan RFM","Pelanggan Teratas"])
with tab1:
    c1,c2=st.columns([1,1])
    with c1:
        fig3=px.pie(summary,names="Segmen",values="Jumlah",hole=.55,color="Segmen",color_discrete_map=COLOR_MAP,template="plotly_dark")
        fig3.update_layout(paper_bgcolor="#0B0B0B",plot_bgcolor="#0B0B0B",font=dict(color="#EAEAEA"),margin=dict(l=10,r=10,t=20,b=10),legend_title_text="Segmen")
        st.plotly_chart(fig3,use_container_width=True)
    with c2:
        st.dataframe(summary[["Segmen","Jumlah","Persentase","Recency","Frequency","Monetary","TotalRevenue"]],use_container_width=True,hide_index=True)
with tab2:
    rfm=summary.melt(id_vars="Segmen",value_vars=["Recency","Frequency","Monetary"],var_name="Metrik",value_name="Nilai")
    fig4=px.bar(rfm,x="Segmen",y="Nilai",color="Metrik",barmode="group",template="plotly_dark")
    fig4.update_layout(paper_bgcolor="#0B0B0B",plot_bgcolor="#0B0B0B",font=dict(color="#EAEAEA"),margin=dict(l=10,r=10,t=20,b=10),legend_title_text="Metrik RFM")
    fig4.update_xaxes(gridcolor="#242424"); fig4.update_yaxes(gridcolor="#242424")
    st.plotly_chart(fig4,use_container_width=True)
with tab3:
    top=filtered.sort_values("Monetary",ascending=False).head(10)[["CustomerID","Segmen","Recency","Frequency","Monetary"]].copy()
    top.insert(0,"Rank",range(1,len(top)+1))
    st.dataframe(top,use_container_width=True,hide_index=True)

st.subheader("📋 Data Pelanggan (Detail)")
st.caption("Data mengikuti filter yang sedang aktif.")
st.dataframe(filtered,use_container_width=True,hide_index=True,height=420)
st.download_button("⬇️ Download Data Hasil Filter (CSV)",data=filtered.to_csv(index=False).encode("utf-8"),file_name="hasil_filter_segmentasi.csv",mime="text/csv",use_container_width=True)

st.subheader("🧠 Insight Otomatis")
best_revenue=summary.loc[summary["TotalRevenue"].idxmax()]; largest=summary.loc[summary["Jumlah"].idxmax()]; best_freq=summary.loc[summary["Frequency"].idxmax()]
st.markdown(f'''<div class="info-card"><div class="info-title">Ringkasan hasil analisis</div><div class="info-text">• Segmen dengan pelanggan terbanyak adalah <b>{largest["Segmen"]}</b> ({largest["Jumlah"]:,.0f} pelanggan / {largest["Persentase"]:.1f}%).<br>• Kontributor revenue terbesar adalah <b>{best_revenue["Segmen"]}</b> dengan revenue sekitar <b>£{best_revenue["TotalRevenue"]:,.0f}</b>.<br>• Segmen dengan rata-rata Frequency tertinggi adalah <b>{best_freq["Segmen"]}</b> ({best_freq["Frequency"]:.1f}x).</div></div>''',unsafe_allow_html=True)
st.markdown('<div class="footer">Dashboard Business Intelligence • RFM + K-Means Clustering</div>',unsafe_allow_html=True)
