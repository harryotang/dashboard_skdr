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


# HEADER
image = Image.open('logo rohil.png')
col1, col2 = st.columns([0.1, 0.9])
with col1:
    st.image(image, width=100)
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


st.markdown("---")

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ==============================
# DASHBOARD PERBANDINGAN TREN PENYAKIT PER TAHUN
# ==============================
st.subheader("📈 Perbandingan Tren Mingguan Kasus Penyakit (2022–2025)")

# --- 1️⃣ Baca data langsung dari file lokal ---
file_path = "data_skdr.xlsx"
excel_data = pd.read_excel(file_path, sheet_name=None)

# Gabungkan semua sheet jadi satu dataframe
df_list = []
for sheet_name, df in excel_data.items():
    df["Tahun"] = int(sheet_name)
    df_list.append(df)
df = pd.concat(df_list, ignore_index=True)

# --- 2️⃣ Pastikan kolom sesuai ---
expected_cols = ["Minggu Ke-", "Nama Penyakit", "Jumlah Kasus"]
if not all(col in df.columns for col in expected_cols):
    st.error(f"Pastikan kolom di tiap sheet adalah: {expected_cols}")
else:
    # --- 3️⃣ Pilihan penyakit & tahun ---
    penyakit_pilih = st.selectbox(
        "🦠 Pilih Nama Penyakit:",
        sorted(df["Nama Penyakit"].unique())
    )

    tahun_tersedia = sorted(df["Tahun"].unique())
    tahun_pilih = st.multiselect(
        "📅 Pilih Tahun untuk Dibandingkan:",
        tahun_tersedia,
        default=tahun_tersedia
    )

    # --- 4️⃣ Filter data sesuai pilihan ---
    df_pilih = df[(df["Nama Penyakit"] == penyakit_pilih) & (df["Tahun"].isin(tahun_pilih))].copy()

    if not df_pilih.empty:
        df_pilih["Minggu Ke-"] = df_pilih["Minggu Ke-"].astype(int)
        minggu_lengkap = pd.DataFrame({"Minggu Ke-": range(1, 54)})

        df_tampil = []
        for tahun in sorted(df_pilih["Tahun"].unique()):
            df_th = df_pilih[df_pilih["Tahun"] == tahun][["Minggu Ke-", "Jumlah Kasus"]]
            df_th = minggu_lengkap.merge(df_th, on="Minggu Ke-", how="left")
            df_th["Jumlah Kasus"] = df_th["Jumlah Kasus"].fillna(0)
            df_th["Tahun"] = tahun
            df_tampil.append(df_th)
        df_final = pd.concat(df_tampil, ignore_index=True)

        # --- 5️⃣ Grafik tren mingguan ---
        fig = go.Figure()

        for tahun in sorted(df_final["Tahun"].unique()):
            df_tahun = df_final[df_final["Tahun"] == tahun]
            fig.add_trace(go.Scatter(
                x=df_tahun["Minggu Ke-"],
                y=df_tahun["Jumlah Kasus"],
                mode="lines+markers",
                name=str(tahun),
                line=dict(width=2)
            ))

            # Tambahkan penanda puncak per tahun
            if df_tahun["Jumlah Kasus"].max() > 0:
                puncak = df_tahun.loc[df_tahun["Jumlah Kasus"].idxmax()]
                fig.add_annotation(
                    x=puncak["Minggu Ke-"],
                    y=puncak["Jumlah Kasus"],
                    text=f"{tahun}: {int(puncak['Jumlah Kasus'])}",
                    showarrow=True,
                    arrowhead=2,
                    ax=0, ay=-25,
                    font=dict(size=11, color="black"),
                    bgcolor="rgba(255,255,255,0.8)",
                    bordercolor="gray",
                    borderwidth=1
                )

        fig.update_layout(
            title=f"📊 Tren Mingguan Kasus {penyakit_pilih} ({', '.join(map(str, tahun_pilih))})",
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


#BATAS CODING

