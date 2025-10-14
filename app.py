import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px

# ==============================
# BACA SEMUA SHEET EXCEL
# ==============================
file_path = "data_skdr.xlsx"
sheets = pd.read_excel(file_path, sheet_name=None)

# Gabungkan semua sheet jadi satu DataFrame dengan pengecekan sheet name
df_all = []
for tahun, data in sheets.items():
    try:
        data["Tahun"] = int(tahun)  # hanya ambil sheet dengan nama angka
    except ValueError:
        print(f"Sheet '{tahun}' dilewati karena nama sheet bukan angka.")
        continue
    df_all.append(data)

df = pd.concat(df_all, ignore_index=True)


# ==============================
# KONFIGURASI DASHBOARD
# ==============================
st.set_page_config(layout="wide", page_title="Dashboard Kesehatan", page_icon="🩺")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)

# HEADER
image = Image.open('logo rohil.png')
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image, width=90)
with col2:
    st.markdown(
        """
        <center><h1 style='font-weight:bold;'>Dashboard Informasi Kesehatan<br>Puskesmas Bangko Kanan</h1></center>
        """,
        unsafe_allow_html=True,
    )

col3, _, _ = st.columns([0.3, 0.4, 0.3])
with col3:
    box_date = datetime.datetime.now().strftime("%d %B %Y")
    st.write(f"📅 **Terakhir diperbarui:** {box_date}")
    st.write("👨‍⚕️ **Dikelola oleh:** Harry Sihotang, SKM")

st.markdown("---")

# ==============================
# FILTER TAHUN
# ==============================
tahun_tersedia = sorted(df["Tahun"].unique())
tahun_pilih = st.selectbox("📆 Pilih Tahun:", tahun_tersedia)
df_filtered = df[df["Tahun"] == tahun_pilih]


# ==============================
# GRAFIK JUMLAH KASUS PER PENYAKIT
# ==============================
st.subheader(f"📊 Jumlah Kasus Berdasarkan Penyakit - Tahun {tahun_pilih}")

fig = px.bar(
    df_filtered,
    x="Nama Penyakit",
    y="Jumlah Kasus",
    color="Nama Penyakit",
    labels={"Jumlah Kasus": "Jumlah Kasus", "Nama Penyakit": "Nama Penyakit"},
    title=f"Distribusi Kasus Penyakit Tahun {tahun_pilih}",
    template="gridon",
    height=450
)
st.plotly_chart(fig, use_container_width=True)


# ==============================
# METRIK UTAMA
# ==============================
colA, colB, colC = st.columns(3)

# Penyakit dengan kasus tertinggi
penyakit_tertinggi = df_filtered.groupby("Nama Penyakit")["Jumlah Kasus"].sum().idxmax()
colA.metric("Penyakit Tertinggi", penyakit_tertinggi)

# Minggu dengan kasus tertinggi
minggu_tertinggi = df_filtered.groupby("Minggu Ke-")["Jumlah Kasus"].sum().idxmax()
colB.metric("Minggu Tertinggi", int(minggu_tertinggi))

# Jumlah kasus pada minggu tertinggi
jumlah_puncak = df_filtered.groupby("Minggu Ke-")["Jumlah Kasus"].sum().max()
colC.metric("Jumlah Kasus pada Puncak", int(jumlah_puncak))


# ==============================
# DOWNLOAD DATA INLINE (HTML link, sejajar)
# ==============================
import base64

data_summary = (
    df_filtered[["Nama Penyakit", "Minggu Ke-", "Jumlah Kasus"]]
    .groupby(["Nama Penyakit", "Minggu Ke-"])
    .sum()
    .reset_index()
)

# Konversi CSV ke base64 agar bisa didownload via link HTML
csv = data_summary.to_csv(index=False)
b64 = base64.b64encode(csv.encode()).decode()

# Buat HTML inline: teks + link download
st.markdown(
    f"""
    <p style='font-size:18px; font-weight:600; margin:0; display:flex; align-items:center;'>
        📋 Data Lengkap Kasus per Minggu - Tahun {tahun_pilih} &nbsp;
        <a href="data:text/csv;base64,{b64}" download="Data_Penyakit_{tahun_pilih}.csv" 
           style='text-decoration:none; background-color:#1f77b4; color:white; padding:2px 4px; border-radius:4px;'>
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

penyakit_pilih = st.selectbox("Pilih Nama Penyakit:", sorted(df_filtered["Nama Penyakit"].unique()))
df_pilih = df_filtered[df_filtered["Nama Penyakit"] == penyakit_pilih].copy()

if not df_pilih.empty:
    df_pilih = df_pilih.sort_values(by="Minggu Ke-")
    df_pilih["Minggu Ke-"] = df_pilih["Minggu Ke-"].astype(int)

    # --- GRAFIK TREND ---
    fig_line = px.line(
        df_pilih,
        x="Minggu Ke-",
        y="Jumlah Kasus",
        markers=True,
        title=f"Tren Mingguan Kasus {penyakit_pilih} Tahun {tahun_pilih}",
        template="gridon",
        height=400,
        color_discrete_sequence=["#1f77b4"]
    )

    for i, row in df_pilih.iterrows():
        fig_line.add_annotation(
            x=row["Minggu Ke-"],
            y=row["Jumlah Kasus"],
            text=str(row["Jumlah Kasus"]),
            showarrow=False,
            font=dict(size=10, color="black"),
            yshift=10
        )

    fig_line.update_xaxes(title_text="Minggu Ke-", dtick=1)
    fig_line.update_yaxes(title_text="Jumlah Kasus")
    st.plotly_chart(fig_line, use_container_width=True)

    # --- RINGKASAN OTOMATIS ---
    total_kasus = int(df_pilih["Jumlah Kasus"].sum())
    minggu_puncak = int(df_pilih.loc[df_pilih["Jumlah Kasus"].idxmax(), "Minggu Ke-"])
    kasus_puncak = int(df_pilih["Jumlah Kasus"].max())

    st.markdown(f"""
    ---
    ### 📊 Ringkasan Data {penyakit_pilih} Tahun {tahun_pilih}
    - **Total kasus sepanjang tahun:** {total_kasus} kasus  
    - **Puncak kasus:** Minggu ke-**{minggu_puncak}** dengan **{kasus_puncak} kasus**
    """)

    # --- DOWNLOAD DATA INLINE (sejajar judul & tombol) ---
    import base64
    csv_penyakit = df_pilih.to_csv(index=False)
    b64_penyakit = base64.b64encode(csv_penyakit.encode()).decode()

    st.markdown(
        f"""
        <p style='font-size:16px; font-weight:600; margin:0; display:flex; align-items:center;'>
            📅 Data Mingguan {penyakit_pilih} - Tahun {tahun_pilih} &nbsp;
            <a href="data:text/csv;base64,{b64_penyakit}" download="Data_{penyakit_pilih}_{tahun_pilih}.csv" 
               style='text-decoration:none; background-color:#1f77b4; color:white; padding:4px 8px; border-radius:4px;'>
               📥 Unduh Data
            </a>
        </p>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("Tidak ada data untuk penyakit ini pada tahun tersebut.")


# ==============================
# DASHBOARD TREND PER MINGGU
# ==============================
st.subheader("📈 Dashboard Pemantauan Penyakit Per Minggu")

# Selectbox dengan key unik agar tidak bentrok
penyakit_pilih = st.selectbox(
    "Pilih Nama Penyakit:",
    sorted(df_filtered["Nama Penyakit"].unique()),
    key="select_penyakit_mingguan"
)

df_pilih = df_filtered[df_filtered["Nama Penyakit"] == penyakit_pilih].copy()

if not df_pilih.empty:
    # --- URUTKAN DAN NORMALISASI MINGGU ---
    df_pilih = df_pilih.sort_values(by="Minggu Ke-")
    df_pilih["Minggu Ke-"] = df_pilih["Minggu Ke-"].astype(int)

    # Normalisasi agar minggu dimulai dari 1
    minggu_min = df_pilih["Minggu Ke-"].min()
    df_pilih["Minggu Normal"] = df_pilih["Minggu Ke-"] - minggu_min + 1

    # --- GRAFIK TREND ---
    import plotly.express as px

    fig_line = px.line(
        df_pilih,
        x="Minggu Normal",
        y="Jumlah Kasus",
        markers=True,
        title=f"Tren Mingguan Kasus {penyakit_pilih} Tahun {tahun_pilih}",
        template="gridon",
        height=400,
        color_discrete_sequence=["#1f77b4"],
        hover_data={
            "Minggu Ke-": True,       # tampilkan minggu asli
            "Minggu Normal": True,    # tampilkan minggu hasil normalisasi
            "Jumlah Kasus": True
        }
    )

    # Tambahkan label di tiap titik data
    for i, row in df_pilih.iterrows():
        fig_line.add_annotation(
            x=row["Minggu Normal"],
            y=row["Jumlah Kasus"],
            text=str(row["Jumlah Kasus"]),
            showarrow=False,
            font=dict(size=10, color="black"),
            yshift=10
        )

    # Atur agar grafik mulai dari minggu ke-1
    fig_line.update_xaxes(
        title_text="Minggu Ke- (Normalisasi)",
        dtick=1,
        range=[0.5, df_pilih["Minggu Normal"].max() + 0.5]
    )
    fig_line.update_yaxes(title_text="Jumlah Kasus")

    st.plotly_chart(fig_line, use_container_width=True)

    # --- RINGKASAN OTOMATIS ---
    total_kasus = int(df_pilih["Jumlah Kasus"].sum())
    minggu_puncak = int(df_pilih.loc[df_pilih["Jumlah Kasus"].idxmax(), "Minggu Normal"])
    kasus_puncak = int(df_pilih["Jumlah Kasus"].max())

    st.markdown(f"""
    ---
    ### 📊 Ringkasan Data {penyakit_pilih} Tahun {tahun_pilih}
    - **Total kasus sepanjang tahun:** {total_kasus} kasus  
    - **Puncak kasus:** Minggu ke-**{minggu_puncak}** dengan **{kasus_puncak} kasus**
    """)

    # --- DOWNLOAD DATA INLINE ---
    import base64
    csv_penyakit = df_pilih.to_csv(index=False)
    b64_penyakit = base64.b64encode(csv_penyakit.encode()).decode()

    st.markdown(
        f"""
        <p style='font-size:16px; font-weight:600; margin:0; display:flex; align-items:center;'>
            📅 Data Mingguan {penyakit_pilih} - Tahun {tahun_pilih} &nbsp;
            <a href="data:text/csv;base64,{b64_penyakit}" 
               download="Data_{penyakit_pilih}_{tahun_pilih}.csv"
               style='text-decoration:none; background-color:#1f77b4; color:white; padding:4px 8px; border-radius:4px;'>
               📥 Unduh Data
            </a>
        </p>
        """,
        unsafe_allow_html=True
    )

else:
    st.info("Tidak ada data untuk penyakit ini pada tahun tersebut.")
