# 🧾 InvoiceIntel: AI-Powered Invoice Extraction

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-red)
![Gemini AI](https://img.shields.io/badge/AI-Gemini%202.0%20Flash-green)
![License](https://img.shields.io/badge/License-MIT-purple)

**InvoiceIntel** is an intelligent automation tool designed to streamline financial data entry. By leveraging Google's **Gemini 2.0 Flash** multimodal capabilities, it transforms unstructured invoice images (JPG, PNG) into structured, analytics-ready Excel data in seconds.

## 🚀 Key Features

* **Multimodal AI Engine:** Accurately reads receipts, invoices, and bills regardless of layout.
* **Structured Output:** Automatically categorizes expenses (F&B, Transport, Utilities, etc.) and extracts dates/amounts strictly.
* **Interactive Dashboard:** Review, edit, and visualize spending directly within the app.
* **Excel Export:** One-click download to integrate with your ERP or Accounting software.
* **Privacy First:** API Keys are managed securely via Streamlit secrets.

## 🛠️ Tech Stack

* **Core:** Python 3.10+
* **Frontend:** Streamlit (for rapid, interactive UI)
* **AI Model:** Google Gemini 2.0 Flash (via `google-generativeai`)
* **Data Processing:** Pandas & OpenPyXL

## ⚙️ Installation & Setup

Follow these steps to run the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/invoice-intel.git
cd invoice-intel

### 2. Clone the Repository
```bash 
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate


### 3. Install Dependencies
```bash
pip install -r requirements.txt


# 4. Setup API Key

## Create a .streamlit folder in the root directory and add a secrets.toml file:

# .streamlit/secrets.toml
GEMINI_API_KEY = "Your_Google_AI_Studio_Key_Here"

#Run the app
````streamlit run app.py````


Usage Workflow

    Launch the app via terminal.

    The app will automatically authenticate using your stored API Key.

    Drag and drop multiple invoice images (e.g., Uber receipts, Restaurant bills).

    Watch the AI extract data in real-time.

    Edit any corrections in the table.

    Download the Clean Excel Report.
