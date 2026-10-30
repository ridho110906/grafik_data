import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Dashboard Kemampuan", page_icon="📊", layout="wide")
st.title("📊 Dashboard Kemampuan Seseorang")
st.caption("Unggah data sendiri atau gunakan data contoh. Grafik dan ringkasan akan mengikuti data yang dipilih.")


def data_contoh():
	return pd.DataFrame(
		[
			{"Nama": nama, "Bidang": bidang, "Kemampuan": kemampuan, "Nilai": nilai,
			 "Tanggal": tanggal, "Kelompok": kelompok}
			for nama, bidang, kemampuan, nilai, tanggal, kelompok in [
				("Andi", "Komunikasi", "Presentasi", 82, "2024-01-10", "Tim A"),
				("Andi", "Teknis", "Python", 76, "2024-02-10", "Tim A"),
				("Andi", "Kepemimpinan", "Koordinasi", 71, "2024-03-10", "Tim A"),
				("Budi", "Komunikasi", "Presentasi", 68, "2024-01-10", "Tim B"),
				("Budi", "Teknis", "Python", 90, "2024-02-10", "Tim B"),
				("Budi", "Kepemimpinan", "Koordinasi", 73, "2024-03-10", "Tim B"),
				("Citra", "Komunikasi", "Presentasi", 93, "2024-01-10", "Tim A"),
				("Citra", "Teknis", "Python", 84, "2024-02-10", "Tim A"),
				("Citra", "Kepemimpinan", "Koordinasi", 88, "2024-03-10", "Tim A"),
				("Dewi", "Komunikasi", "Presentasi", 79, "2024-01-10", "Tim B"),
				("Dewi", "Teknis", "Python", 72, "2024-02-10", "Tim B"),
				("Dewi", "Kepemimpinan", "Koordinasi", 95, "2024-03-10", "Tim B"),
			]
		]
	)


with st.sidebar:
	st.header("Sumber data")
	file_data = st.file_uploader("Unggah file CSV", type=["csv"])
	if file_data:
		try:
			df = pd.read_csv(file_data)
		except Exception as exc:
			st.error(f"CSV tidak dapat dibaca: {exc}")
			st.stop()
	else:
		df = data_contoh()
		st.info("Menampilkan data contoh. Unggah CSV untuk memakai data sendiri.")

if df.empty or len(df.columns) == 0:
	st.warning("Data kosong atau tidak memiliki kolom.")
	st.stop()

df = df.dropna(how="all").copy()
kolom = list(df.columns)
numeric_cols = list(df.select_dtypes(include="number").columns)
if not numeric_cols:
	st.warning("Data memerlukan minimal satu kolom numerik untuk membuat grafik.")
	st.dataframe(df, use_container_width=True)
	st.stop()

with st.sidebar:
	st.header("Pengaturan")
	chart = st.selectbox(
		"Jenis grafik",
		["Bar chart", "Column chart", "Line chart", "Area chart", "Pie chart",
		 "Treemap", "Scatter plot", "Bubble chart", "Histogram", "Box plot"],
	)
	x_default = kolom.index("Bidang") if "Bidang" in kolom else 0
	y_default = numeric_cols.index("Nilai") if "Nilai" in numeric_cols else 0
	kategori = st.selectbox("Kategori / sumbu X", kolom, index=x_default)
	nilai = st.selectbox("Nilai numerik / sumbu Y", numeric_cols, index=y_default)
	warna_opsi = ["(tanpa warna)"] + [c for c in kolom if c != nilai]
	warna = st.selectbox("Warna (opsional)", warna_opsi)
	warna = None if warna == "(tanpa warna)" else warna

	nama_kolom = st.selectbox("Filter orang (opsional)", ["(semua)"] + kolom)
	if nama_kolom != "(semua)":
		tersedia = df[nama_kolom].dropna().astype(str).unique().tolist()
		pilihan = st.multiselect("Pilih nilai", tersedia, default=tersedia)
		df = df[df[nama_kolom].astype(str).isin(pilihan)]

if df.empty:
	st.warning("Tidak ada data yang cocok dengan filter.")
	st.stop()

st.subheader("Ringkasan data")
m1, m2, m3 = st.columns(3)
m1.metric("Jumlah data", f"{len(df):,}")
m2.metric("Rata-rata nilai", f"{df[nilai].mean():.1f}")
m3.metric("Nilai tertinggi", f"{df[nilai].max():.1f}")

st.subheader(chart)
try:
	if chart in ("Bar chart", "Column chart"):
		ringkas = df.groupby(kategori, as_index=False, dropna=False)[nilai].mean()
		fig = px.bar(ringkas, x=kategori, y=nilai, color=warna if warna in ringkas.columns else None,
					 title=f"Rata-rata {nilai} berdasarkan {kategori}")
		if chart == "Bar chart":
			fig.update_layout(xaxis_title=nilai, yaxis_title=kategori)
			fig.update_traces(orientation="h", x=ringkas[nilai], y=ringkas[kategori])
	elif chart == "Line chart":
		fig = px.line(df, x=kategori, y=nilai, color=warna, markers=True)
	elif chart == "Area chart":
		fig = px.area(df, x=kategori, y=nilai, color=warna)
	elif chart == "Pie chart":
		pie_data = df.groupby(kategori, as_index=False, dropna=False)[nilai].sum()
		fig = px.pie(pie_data, names=kategori, values=nilai)
	elif chart == "Treemap":
		hierarki = st.sidebar.multiselect(
			"Tingkat hierarki treemap", [c for c in kolom if c != nilai],
			default=[kategori] if kategori != nilai else [],
		)
		if not hierarki:
			st.warning("Pilih minimal satu kolom hierarki untuk treemap.")
			st.stop()
		fig = px.treemap(df, path=hierarki, values=nilai, color=nilai)
	elif chart == "Scatter plot":
		x_num = st.sidebar.selectbox("Sumbu X numerik", numeric_cols, index=0)
		fig = px.scatter(df, x=x_num, y=nilai, color=warna, hover_data=kolom)
	elif chart == "Bubble chart":
		x_num = st.sidebar.selectbox("Sumbu X numerik", numeric_cols, index=0)
		ukuran = st.sidebar.selectbox("Ukuran gelembung", numeric_cols, index=y_default)
		fig = px.scatter(df, x=x_num, y=nilai, size=ukuran, color=warna, hover_data=kolom)
	elif chart == "Histogram":
		fig = px.histogram(df, x=nilai, color=warna, nbins=20)
	else:
		fig = px.box(df, x=kategori, y=nilai, color=warna, points="all")

	fig.update_layout(template="plotly_white", margin=dict(l=20, r=20, t=55, b=20))
	st.plotly_chart(fig, use_container_width=True)
except (ValueError, KeyError, TypeError) as exc:
	st.error(f"Grafik tidak dapat dibuat dari kombinasi kolom ini: {exc}")

with st.expander("Lihat data yang digunakan"):
	st.dataframe(df, use_container_width=True)
