import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json
import io

# --- 1. PRODUCT CONFIGURATION ---
st.set_page_config(
    page_title="InvoiceIntel | AI Expense Tracker",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a cleaner look
st.markdown("""
<style>
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: bold;
    }
    .main-header {
        font-size: 2.5rem;
        color: #4B4B4B;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. AUTHENTICATION & SIDEBAR ---
with st.sidebar:
    st.title("🧾 InvoiceIntel")
    st.caption("v1.0.0 | Powered by Gemini 2.0 Flash")
    st.markdown("---")
    
    st.markdown("### ⚙️ Configuration")
    
    # Secure API Key Management
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
        st.success("✅ API Key Authenticated")
    else:
        api_key = st.text_input("Gemini API Key", type="password", help="Get your key at aistudio.google.com")
        if not api_key:
            st.warning("⚠️ Please enter your API Key to proceed.")
            st.stop()

    st.markdown("---")
    st.markdown("### 📖 How it works")
    st.info(
        """
        1. **Upload** your invoices (Images).
        2. **AI Extracts** key data (Vendor, Date, Total).
        3. **Review** the structured table.
        4. **Export** to Excel for your finance team.
        """
    )

# --- 3. AI ENGINE (CORE LOGIC) ---
def extract_invoice_data(image, api_key):
    """Sends image to Gemini 2.0 Flash and expects a strictly formatted JSON response."""
    try:
        genai.configure(api_key=api_key)
        # Using the latest fast model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = """
        You are an expert Financial Data Extraction AI.
        
        Task: Analyze the provided invoice/receipt image and extract key information.
        
        Output Requirement:
        - Return ONLY a valid JSON object.
        - Do not include markdown formatting (like ```json).
        - If a field is missing, use null.
        
        JSON Structure:
        {
            "date": "YYYY-MM-DD (format strictly)",
            "vendor_name": "String (e.g., Uber, Starbucks, AWS)",
            "category": "String (Choose strictly from: F&B, Transportation, Office Supplies, Utilities, Software, Other)",
            "total_amount": Number (Float/Int, remove currency symbols),
            "currency": "String (e.g., IDR, USD, SGD)",
            "invoice_number": "String (or null)"
        }
        """
        
        response = model.generate_content([prompt, image])
        
        # Clean potential markdown formatting from AI response
        clean_text = response.text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
        
    except Exception as e:
        st.error(f"Extraction failed: {e}")
        return None

# --- 4. MAIN INTERFACE ---
st.markdown('<p class="main-header">🧾 AI Invoice Extraction Agent</p>', unsafe_allow_html=True)
st.markdown("Transform messy receipt photos into structured Excel data instantly.")

col1, col2 = st.columns([1, 1.5], gap="large")

with col1:
    st.subheader("📤 Upload Documents")
    uploaded_files = st.file_uploader(
        "Drag and drop receipts here", 
        accept_multiple_files=True, 
        type=['png', 'jpg', 'jpeg']
    )

# Data container
all_extracted_data = []

with col2:
    if uploaded_files and api_key:
        st.subheader("🧠 Live Extraction Status")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, file in enumerate(uploaded_files):
            status_text.text(f"Processing: {file.name}...")
            
            # Load and process image
            image = Image.open(file)
            data = extract_invoice_data(image, api_key)
            
            if data:
                data['source_file'] = file.name
                all_extracted_data.append(data)
            
            # Update UI
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        status_text.text("✅ Processing Complete!")
        progress_bar.empty()

# --- 5. ANALYTICS & EXPORT SECTION ---
if all_extracted_data:
    st.divider()
    
    # Convert to DataFrame
    df = pd.read_json(json.dumps(all_extracted_data))
    
    # Data Cleaning: Convert Date
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors='coerce')
    
    # 5.1. Dashboard Metrics
    st.subheader("📊 Financial Overview")
    m1, m2, m3 = st.columns(3)
    
    total_spend = df['total_amount'].sum() if 'total_amount' in df.columns else 0
    top_cat = df['category'].mode()[0] if 'category' in df.columns and not df.empty else "N/A"
    
    m1.metric("Total Extracted", f"{len(df)} Invoices")
    m2.metric("Total Spending", f"{total_spend:,.0f}")
    m3.metric("Top Category", top_cat)

    # 5.2. Interactive Data Editor
    st.subheader("📝 Review & Edit Data")
    edited_df = st.data_editor(
        df,
        column_config={
            "total_amount": st.column_config.NumberColumn("Amount", format="%.2f"),
            "date": st.column_config.DateColumn("Date", format="DD/MM/YYYY"),
            "category": st.column_config.SelectboxColumn(
                "Category",
                options=["F&B", "Transportation", "Office Supplies", "Utilities", "Software", "Other"],
                required=True
            ),
            "vendor_name": "Vendor",
            "currency": "Curr",
            "invoice_number": "Invoice #"
        },
        use_container_width=True,
        num_rows="dynamic"
    )
    
    # 5.3. Visualization
    if not edited_df.empty:
        st.bar_chart(edited_df, x="category", y="total_amount", color="category")

    # 5.4. Excel Export Logic
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        # Format date as string for Excel compatibility
        export_df = edited_df.copy()
        export_df['date'] = export_df['date'].dt.strftime('%Y-%m-%d')
        export_df.to_excel(writer, index=False, sheet_name='Invoices')
        
    st.download_button(
        label="📥 Download Report (.xlsx)",
        data=buffer.getvalue(),
        file_name="Invoice_Report_Final.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        type="primary"
    )

elif not uploaded_files:
    st.info("👈 Waiting for uploads... Please add your receipt images.")