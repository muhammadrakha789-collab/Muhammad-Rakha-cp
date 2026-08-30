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

st.set_page_config(page_title="Dashboard Segmentasi Pelanggan", layout="wide")

COLOR_MAP = {
    "Champions": "#B8862B",
    "Promising/New Active": "#2C7A70",
    "At Risk": "#C1651A",
    "Lost/Churned": "#A63D40",
}

@st.cache_data
def load_data():
    df = pd.read_csv("rfm_segmentasi_pelanggan.csv")
    return df

df = load_data()

st.title("📊 Dashboard Segmentasi Pelanggan E-Commerce")
st.caption("Metode: RFM (Recency, Frequency, Monetary) + K-Means Clustering")

# --- Sidebar filter ---
st.sidebar.header("Filter")
segments = st.sidebar.multiselect(
    "Pilih Segmen",
    options=sorted(df["Segmen"].unique()),
    default=sorted(df["Segmen"].unique()),
)
filtered = df[df["Segmen"].isin(segments)]

# --- KPI cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Pelanggan", f"{len(filtered):,}")
col2.metric("Total Revenue", f"£{filtered['Monetary'].sum():,.0f}")
col3.metric("Rata-rata Frequency", f"{filtered['Frequency'].mean():.1f}x")
col4.metric("Rata-rata Recency", f"{filtered['Recency'].mean():.0f} hari")

st.divider()

# --- Ringkasan per segmen ---
summary = (
    filtered.groupby("Segmen")
    .agg(
        Jumlah=("CustomerID", "count"),
        Recency=("Recency", "mean"),
        Frequency=("Frequency", "mean"),
        Monetary=("Monetary", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    .round(1)
    .reset_index()
)
summary["Persentase"] = (summary["Jumlah"] / summary["Jumlah"].sum() * 100).round(1)

col_a, col_b = st.columns([1.3, 1])

with col_a:
    st.subheader("Sebaran Pelanggan: Recency vs Monetary")
    fig = px.scatter(
        filtered.sample(min(1500, len(filtered)), random_state=42),
        x="Recency", y="Monetary", color="Segmen", size="Frequency",
        color_discrete_map=COLOR_MAP, log_y=True, opacity=0.6,
        hover_data=["CustomerID"],
    )
    st.plotly_chart(fig, use_container_width=True)

with col_b:
    st.subheader("Kontribusi Revenue per Segmen")
    fig2 = px.bar(
        summary.sort_values("TotalRevenue"), x="TotalRevenue", y="Segmen",
        orientation="h", color="Segmen", color_discrete_map=COLOR_MAP, text="TotalRevenue",
    )
    fig2.update_traces(texttemplate="£%{text:,.0f}", textposition="outside")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("Tabel Ringkasan Segmen")
st.dataframe(
    summary[["Segmen", "Jumlah", "Persentase", "Recency", "Frequency", "Monetary", "TotalRevenue"]],
    use_container_width=True, hide_index=True,
)

st.subheader("Data Pelanggan (Detail)")
st.dataframe(filtered, use_container_width=True, hide_index=True)
