import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go
import base64

# ==============================
# KONFIGURASI DASAR
# ==============================
st.set_page_config(layout="wide", page_title="Dashboard Kesehatan", page_icon="🩺")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# ==============================
# BACA DATA DARI GOOGLE SHEETS
# ==============================
sheet_url = "https://docs.google.com/spreadsheets/d/1pYdy6fjiNM8dBVBrUzje4tW9gvvUKwN4fPu_r0MZThk/export?format=csv&gid=1786208895"

try:
    df_raw = pd.read_csv(sheet_url)
except Exception as e:
    st.error(f"❌ Gagal membaca data dari Google Sheets: {e}")
    st.stop()

# ==============================
# PEMBERSIHAN DATA
# ==============================
df_raw.columns = df_raw.columns.str.strip()
for col in ["Nama Penyakit"]:
    df_raw[col] = df_raw[col].astype(str).str.strip()

for col in ["Tahun", "Minggu Ke-", "Jumlah Kasus"]:
    df_raw[col] = pd.to_numeric(df_raw[col], errors="coerce").fillna(0).astype(int)

df = df_raw.copy()

expected_cols = ["Minggu Ke-", "Nama Penyakit", "Jumlah Kasus", "Tahun"]
if not all(col in df.columns for col in expected_cols):
    st.error(f"❌ Pastikan spreadsheet memiliki kolom: {expected_cols}")
    st.stop()

# ==============================
# HEADER
# ==============================
try:
    image = Image.open('logo rohil.png')
    col1, col2 = st.columns([0.1, 0.9])
    with col1:
        st.image(image, width=100)
    with col2:
        st.markdown("""
            <center><h1 style='font-weight:bold;'>
            Dashboard Informasi Kesehatan<br>Puskesmas Bangko Kanan
            </h1></center>
        """, unsafe_allow_html=True)
except:
    st.markdown("""
        <center><h1 style='font-weight:bold;'>
        Dashboard Informasi Kesehatan<br>Puskesmas Bangko Kanan
        </h1></center>
    """, unsafe_allow_html=True)

col3, _, _ = st.columns([0.3, 0.4, 0.3])
with col3:
    st.write(f"📅 **Terakhir diperbarui:** {datetime.datetime.now().strftime('%d %B %Y')}")
    st.write("👨‍⚕️ **Dikelola oleh:** Harry Sihotang, SKM")

st.markdown("---")

# ==============================
# FILTER TAHUN
# ==============================
tahun_tersedia = sorted(df["Tahun"].unique())
tahun_pilih = st.selectbox("📆 Pilih Tahun:", tahun_tersedia)
df_filtered = df[df["Tahun"] == tahun_pilih]

# ==============================
# GRAFIK JUMLAH KASUS PER PENYAKIT (BAR + PIE)
# ==============================
st.subheader(f"📊 Jumlah Kasus Berdasarkan Penyakit - Tahun {tahun_pilih}")

# 🔧 PERBAIKAN: logika sorting disesuaikan agar berfungsi
sort_option = st.radio(
    "Urutkan berdasarkan jumlah kasus:",
    ("Tertinggi", "Terendah"),
    horizontal=True
)

df_bar = df_filtered.groupby("Nama Penyakit", as_index=False)["Jumlah Kasus"].sum()

if sort_option == "Tertinggi":
    df_bar = df_bar.sort_values(by="Jumlah Kasus", ascending=False)
else:
    df_bar = df_bar.sort_values(by="Jumlah Kasus", ascending=True)

col_bar, col_pie = st.columns(2)

# ====== BAR CHART ======
with col_bar:
    fig_bar = px.bar(
        df_bar,
        x="Nama Penyakit",
        y="Jumlah Kasus",
        color="Nama Penyakit",
        labels={"Jumlah Kasus": "Jumlah Kasus", "Nama Penyakit": "Nama Penyakit"},
        title=f"Distribusi Kasus Penyakit Tahun {tahun_pilih}",
        template="gridon",
        height=500
    )
    fig_bar.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(t=50, b=50, l=40, r=20)
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# ====== PIE CHART ======
with col_pie:
    if not df_bar.empty:
        total = df_bar["Jumlah Kasus"].sum()
        df_bar["Persen"] = (df_bar["Jumlah Kasus"] / total) * 100
        df_bar["Label Lengkap"] = df_bar.apply(
            lambda x: f"{x['Nama Penyakit']} ({x['Persen']:.1f}%)".replace(".0%", "%"),
            axis=1
        )

        fig_pie = go.Figure(data=[go.Pie(
            labels=df_bar["Label Lengkap"],
            values=df_bar["Jumlah Kasus"],
            text=df_bar["Label Lengkap"],
            textinfo="text",
            textposition="outside",
            insidetextorientation="radial",
            hole=0.4,
            pull=[0.05]*len(df_bar),
            marker=dict(line=dict(color="white", width=2)),
            showlegend=False,
            hovertemplate="%{label}<br>Jumlah: %{value}<extra></extra>"
        )])

        fig_pie.update_layout(
            title=f"Persentase Kasus Penyakit Tahun {tahun_pilih}",
            height=500,
            margin=dict(t=50, b=50, l=50, r=50),
            uniformtext_minsize=12,
            showlegend=False
        )

        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("Tidak ada data penyakit pada tahun ini.")

# ==============================
# METRIK UTAMA
# ==============================
colA, colB, colC = st.columns(3)
try:
    penyakit_tertinggi = df_filtered.groupby("Nama Penyakit")["Jumlah Kasus"].sum().idxmax()
    minggu_tertinggi = df_filtered.groupby("Minggu Ke-")["Jumlah Kasus"].sum().idxmax()
    jumlah_puncak = df_filtered.groupby("Minggu Ke-")["Jumlah Kasus"].sum().max()

    colA.metric("Penyakit Tertinggi", penyakit_tertinggi)
    colB.metric("Minggu Tertinggi", int(minggu_tertinggi))
    colC.metric("Jumlah Kasus pada Puncak", int(jumlah_puncak))
except Exception as e:
    st.warning(f"⚠️ Data tidak lengkap: {e}")

# ==============================
# DOWNLOAD DATA TAHUNAN
# ==============================
data_summary = (
    df_filtered[["Nama Penyakit", "Minggu Ke-", "Jumlah Kasus"]]
    .groupby(["Nama Penyakit", "Minggu Ke-"])
    .sum()
    .reset_index()
)
csv = data_summary.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()

st.markdown(
    f"""
    <p style='font-size:18px; font-weight:600;'>
        📋 Data Lengkap Kasus per Minggu - Tahun {tahun_pilih} &nbsp;
        <a href="data:text/csv;base64,{b64}" download="Data_Penyakit_{tahun_pilih}.csv"
           style='text-decoration:none; background-color:#1f77b4; color:white; padding:4px 8px; border-radius:4px;'>
           📥 Unduh Data
        </a>
    </p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ==============================
# DASHBOARD TREND PER MINGGU
# ==============================
st.subheader("📈 Dashboard Pemantauan Penyakit Per Minggu")

penyakit_pilih = st.selectbox(
    "Pilih Nama Penyakit:",
    sorted(df_filtered["Nama Penyakit"].unique()),
    key="select_penyakit_mingguan"
)

df_pilih = df_filtered[df_filtered["Nama Penyakit"] == penyakit_pilih].copy()
if not df_pilih.empty:
    df_pilih = df_pilih.sort_values(by="Minggu Ke-")
    df_pilih = pd.DataFrame({"Minggu Ke-": range(1, 54)}).merge(
        df_pilih, on="Minggu Ke-", how="left"
    ).fillna(0)
    df_pilih["Jumlah Kasus"] = df_pilih["Jumlah Kasus"].astype(int)
    df_pilih["Minggu Normal"] = df_pilih["Minggu Ke-"]

    fig_line = px.line(
        df_pilih,
        x="Minggu Normal",
        y="Jumlah Kasus",
        markers=True,
        title=f"Tren Mingguan Kasus {penyakit_pilih} Tahun {tahun_pilih}",
        template="gridon",
        height=400,
        color_discrete_sequence=["#1f77b4"]
    )

    for i, row in df_pilih.iterrows():
        fig_line.add_annotation(
            x=row["Minggu Normal"],
            y=row["Jumlah Kasus"],
            text=str(row["Jumlah Kasus"]),
            showarrow=False,
            font=dict(size=10, color="black"),
            yshift=10
        )

    fig_line.update_xaxes(dtick=1, range=[0.5, 53.5])
    st.plotly_chart(fig_line, use_container_width=True)

    total_kasus = int(df_pilih["Jumlah Kasus"].sum())
    minggu_puncak = int(df_pilih.loc[df_pilih["Jumlah Kasus"].idxmax(), "Minggu Normal"])
    kasus_puncak = int(df_pilih["Jumlah Kasus"].max())

    st.markdown(f"""
    ### 📊 Ringkasan Data {penyakit_pilih} Tahun {tahun_pilih}
    - **Total kasus sepanjang tahun:** {total_kasus} kasus  
    - **Puncak kasus:** Minggu ke-**{minggu_puncak}** dengan **{kasus_puncak} kasus**
    """)
else:
    st.info("Tidak ada data untuk penyakit ini pada tahun tersebut.")

st.markdown("---")

# ==============================
# PERBANDINGAN TREN ANTAR TAHUN
# ==============================
st.subheader("📈 Perbandingan Tren Mingguan Kasus Penyakit (2022–2025)")

penyakit_banding = st.selectbox(
    "🦠 Pilih Nama Penyakit untuk dibandingkan:",
    sorted(df["Nama Penyakit"].unique())
)
tahun_pilih_multi = st.multiselect(
    "📅 Pilih Tahun untuk Dibandingkan:",
    sorted(df["Tahun"].unique()),
    default=sorted(df["Tahun"].unique())
)

df_multi = df[(df["Nama Penyakit"] == penyakit_banding) & (df["Tahun"].isin(tahun_pilih_multi))].copy()
if not df_multi.empty:
    df_multi = pd.DataFrame({"Minggu Ke-": range(1, 54)}).merge(
        df_multi, on="Minggu Ke-", how="left"
    ).fillna(0)
    df_multi["Jumlah Kasus"] = df_multi["Jumlah Kasus"].astype(int)

    fig = go.Figure()
    for th in sorted(df_multi["Tahun"].unique()):
        df_th = df_multi[df_multi["Tahun"] == th]
        fig.add_trace(go.Scatter(
            x=df_th["Minggu Ke-"],
            y=df_th["Jumlah Kasus"],
            mode="lines+markers",
            name=str(th),
            line=dict(width=2)
        ))
        if df_th["Jumlah Kasus"].max() > 0:
            puncak = df_th.loc[df_th["Jumlah Kasus"].idxmax()]
            fig.add_annotation(
                x=puncak["Minggu Ke-"],
                y=puncak["Jumlah Kasus"],
                text=f"{th}: {int(puncak['Jumlah Kasus'])}",
                showarrow=True,
                arrowhead=2,
                ax=0, ay=-25,
                font=dict(size=11, color="black"),
                bgcolor="rgba(255,255,255,0.8)"
            )

    fig.update_layout(
        title=f"📊 Tren Mingguan Kasus {penyakit_banding} ({', '.join(map(str, tahun_pilih_multi))})",
        xaxis_title="Minggu Ke-",
        yaxis_title="Jumlah Kasus",
        xaxis=dict(dtick=1, range=[1, 53]),
        legend_title_text="Tahun",
        template="gridon",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Tidak ada data untuk kombinasi penyakit dan tahun yang dipilih.")
