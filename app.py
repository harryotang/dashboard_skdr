import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go


#reading the data from excel file
df = pd.read_excel("data_skdr.xlsx")
st.set_page_config(layout="wide")
st.markdown('<style>div.block-container{padding-top1:rem;}</style>',unsafe_allow_html=True)
image = Image.open('logo rohil.png')

col1, col2 = st.columns([0.1,0.9])
with col1:
    st.image(image,width=100)

html_title = """
    <style>
    .title-test {
    font-weight:bold;
    padding:5px;
    border-radius:6px;
    }
    </style>
    <center><h1 class="title-test">Dashboard Informasi Kesehatan Puskesmas Bangko Kanan</h1></center>"""
with col2:
    st.markdown(html_title, unsafe_allow_html=True)

col3, col4, col5 = st.columns([0.1,0.45,0.45])
with col3:
    box_date = str(datetime.datetime.now().strftime("%d %B %Y"))
    st.write(f"Last updated by: \n {box_date}")

with col4:
    fig = px.bar(df, x = "Nama Penyakit", y = "Jumlah Kasus", labels={"Jumlah Kasus"},
                 title= "Jumlah Kasus berdasarkan Penyakit", hover_data=["Jumlah Kasus"],
                  template="gridon",height=500)
    st.plotly_chart(fig,use_container_width=True)

_, view1, dwn1, view2, dwn2 = st.columns([0.15,0.20,0.20,0.20,0.20])
with view1:
    expander = st.expander("Informasi Penyakit Per Minggu")
    data = df[["Nama Penyakit","Minggu Ke-","Jumlah Kasus"]].groupby(by=["Nama Penyakit","Minggu Ke-"])["Jumlah Kasus"].sum()
    expander.write(data)
with dwn1:
    st.download_button("Get Data", data = data.to_csv().encode("utf-8"),
                       file_name="Informasi Penyakit.csv", mime="text/csv")
    
#batas coding#

st.subheader("📈 Dashboard Pemantauan Penyakit per Minggu")

# Pilih nama penyakit
penyakit_pilih = st.selectbox("Pilih Nama Penyakit:", sorted(df["Nama Penyakit"].unique()))

# Filter data sesuai pilihan penyakit
df_pilih = df[df["Nama Penyakit"] == penyakit_pilih].copy()

# Pastikan minggu dalam urutan benar dan mulai dari 1
df_pilih = df_pilih.sort_values(by="Minggu Ke-")
df_pilih["Minggu Ke-"] = df_pilih["Minggu Ke-"].astype(int)

# Buat grafik garis
fig_line = px.line(
    df_pilih,
    x="Minggu Ke-",
    y="Jumlah Kasus",
    markers=True,
    title=f"Tren Jumlah Kasus {penyakit_pilih} per Minggu",
    template="gridon",
    height=350
)

# Tambahkan label angka di setiap titik
for i, row in df_pilih.iterrows():
    fig_line.add_annotation(
        x=row["Minggu Ke-"],
        y=row["Jumlah Kasus"],
        text=str(row["Jumlah Kasus"]),
        showarrow=False,
        font=dict(size=10, color="black"),
        yshift=10
    )

# Ubah tampilan sumbu dan layout
fig_line.update_xaxes(
    title_text="Minggu Ke-",
    dtick=1,              # tampilkan setiap minggu
    range=[0.5, df_pilih["Minggu Ke-"].max() + 0.5]  # mulai dari minggu 1
)
fig_line.update_yaxes(title_text="Jumlah Kasus")

fig_line.update_layout(
    title_font=dict(size=16, color="black"),
    xaxis_title_font=dict(size=11),
    yaxis_title_font=dict(size=11),
    margin=dict(l=30, r=30, t=50, b=40),
)

# Tampilkan grafik
st.plotly_chart(fig_line, use_container_width=True)

# Kolom data dan tombol unduh
colA, colB = st.columns([0.8, 0.2])
with colA:
    expander = st.expander("📊 Data Mingguan")
    expander.write(df_pilih[["Minggu Ke-", "Jumlah Kasus"]])
with colB:
    st.download_button(
        "📥 Unduh Data",
        data=df_pilih.to_csv(index=False).encode("utf-8"),
        file_name=f"Data_{penyakit_pilih}_PerMinggu.csv",
        mime="text/csv"
    )
