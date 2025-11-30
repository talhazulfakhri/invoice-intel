import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import io

# --- 1. CONFIGURATION ---
st.set_page_config(page_title="InvoiceIntel", page_icon="🧾", layout="wide")

# Custom CSS biar tombolnya lebih catchy
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR SETUP ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2921/2921222.png", width=50)
    st.title("InvoiceIntel")
    st.markdown("Automasi input data dari foto struk/invoice menjadi Excel.")
    st.divider()
    
    # LOGIKA OTOMATIS: Cek dulu di secrets, kalau ga ada baru minta input
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("✅ API Key terdeteksi otomatis!")
    else:
        api_key = st.text_input("🔑 Masukkan Gemini API Key", type="password")
        if not api_key:
            st.warning("⚠️ Masukkan API Key dulu untuk mulai.")
            st.stop()

# --- 3. THE AI BRAIN (FUNCTION) ---
def extract_invoice_data(image, api_key):
    """Mengirim gambar ke Gemini Flash dan minta balik json"""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """
        Peranmu adalah Data Entry Specialist Expert.
        Tugas: Analisa gambar invoice/struk ini dan ekstrak datanya.
        
        Aturan Output:
        Kembalikan HANYA JSON object murni tanpa format markdown (```json ... ```).
        Jangan ada teks lain.
        
        Struktur JSON wajib:
        {
            "tanggal": "YYYY-MM-DD (jika tidak ada, null)",
            "nama_vendor": "String (contoh: Starbucks, Tokopedia)",
            "kategori": "Pilih satu: [Makan & Minum, Transportasi, Belanja Kantor, Utilitas, Lainnya]",
            "total_bayar": Integer (Hanya angka, hilangkan Rp/USD/titik/koma),
            "mata_uang": "String (IDR/USD)",
            "no_invoice": "String (atau null)"
        }
        """
        
        response = model.generate_content([prompt, image])
        
        # Bersihin hasil kalau AI ngasih markdown backticks
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"Gagal memproses gambar: {e}")
        return None

# --- 4. MAIN INTERFACE ---
st.header("🧾 Upload Invoice/Struk Belanja")
st.caption("Support: JPG, PNG, JPEG")

col1, col2 = st.columns([1, 1.5])

with col1:
    uploaded_files = st.file_uploader("Drop file di sini", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

# Container buat nampung hasil
all_extracted_data = []

with col2:
    if uploaded_files and api_key:
        st.subheader("⏳ Processing...")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Loop setiap file yang diupload
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Membaca file: {file.name}...")
            
            # Buka gambar
            image = Image.open(file)
            
            # Panggil AI
            data = extract_invoice_data(image, api_key)
            
            if data:
                data['nama_file'] = file.name # Tambahin nama file asli
                all_extracted_data.append(data)
            
            # Update progress bar
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("✅ Selesai!")
        progress_bar.empty()

# --- 5. RESULT & EXPORT SECTION ---
if all_extracted_data:
    st.divider()
    st.subheader("📊 Hasil Ekstraksi Data")
    
    # Bikin DataFrame Pandas
    df = pd.read_json(json.dumps(all_extracted_data))
    
    # FIX DATE FORMAT: Ubah string jadi datetime object
    if "tanggal" in df.columns:
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors='coerce')

    # Tampilkan Tabel Interaktif
    st.data_editor(
        df,
        column_config={
            "total_bayar": st.column_config.NumberColumn(
                "Total Bayar",
                format="Rp %d", 
            ),
            "tanggal": st.column_config.DateColumn(
                "Tanggal Transaksi",
                format="DD/MM/YYYY" # Biar formatnya enak dibaca orang Indo
            ),
            "kategori": st.column_config.SelectboxColumn(
                "Kategori",
                options=["Makan & Minum", "Transportasi", "Belanja Kantor", "Utilitas", "Lainnya"]
            )
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    # --- VISUALISASI SIMPLE ---
    st.write("")
    col_metric1, col_metric2 = st.columns(2)
    with col_metric1:
        # Handle kalau total_bayar ternyata bukan angka
        if "total_bayar" in df.columns:
            total_spending = df['total_bayar'].sum()
            st.metric("Total Pengeluaran", f"Rp {total_spending:,.0f}")
    
    with col_metric2:
        if "kategori" in df.columns and "total_bayar" in df.columns:
            st.caption("Pengeluaran per Kategori")
            st.bar_chart(df.groupby("kategori")["total_bayar"].sum())

    # --- TOMBOL DOWNLOAD ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Saat export ke excel, ubah tanggal jadi string lagi biar excel gak bingung
        df_export = df.copy()
        df_export['tanggal'] = df_export['tanggal'].dt.strftime('%Y-%m-%d')
        df_export.to_excel(writer, index=False, sheet_name='Laporan Keuangan')
        
    st.download_button(
        label="📥 Download Laporan Excel (.xlsx)",
        data=buffer.getvalue(),
        file_name="Laporan_Invoice_AI.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

elif not uploaded_files:
    st.info("👈 Upload dulu gambarnya di sebelah kiri ya.")