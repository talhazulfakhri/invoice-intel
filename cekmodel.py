import google.generativeai as genai

# Minta input API Key biar aman
api_key = input("Paste API Key kamu di sini lalu tekan Enter: ")
genai.configure(api_key=api_key)

print("\nSedang menghubungi Google... mohon tunggu...")

try:
    print("\n=== DAFTAR MODEL YANG TERSEDIA UNTUK KAMU ===")
    found = False
    for m in genai.list_models():
        # Kita cari model yang bisa generateContent (text/gambar)
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ {m.name}")
            found = True
            
    if not found:
        print("❌ Tidak ada model yang ditemukan. Cek API Key atau Region.")
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("Pastikan internet nyambung dan API Key benar.")