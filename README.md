# 💰 API Rekomendasi Keuangan — Powered by Google Gemini AI

REST API untuk sistem rekomendasi pengeluaran berbasis AI. Dibangun dengan FastAPI + Google Gemini.

---

## 🚀 Endpoints

| Method | URL | Fungsi |
|--------|-----|--------|
| GET | `/health` | Cek status server |
| POST | `/rekomendasi` | Analisis transaksi + rekomendasi AI |
| POST | `/chatbot` | Tanya jawab keuangan bebas |
| GET | `/docs` | Swagger UI (dokumentasi interaktif) |

---

## 📦 Struktur File

```
api_rekomendasi/
├── main.py            ← FastAPI app utama
├── requirements.txt   ← Dependensi Python
├── .env.example       ← Template environment variable
├── .gitignore
└── README.md
```

---

## 🔧 Cara Deploy (Step-by-Step)

### LANGKAH 1 — Dapatkan Gemini API Key

1. Buka [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)
2. Login dengan akun Google
3. Klik **"Create API Key"**
4. Salin key-nya (bentuk: `AIzaSy...`) — simpan, jangan share

---

### LANGKAH 2 — Upload ke GitHub

1. Buka [https://github.com](https://github.com) → Login
2. Klik tombol **"New repository"** (pojok kanan atas)
3. Isi:
   - Repository name: `api-rekomendasi-keuangan`
   - Visibility: **Public**
   - Jangan centang "Add README" (sudah ada)
4. Klik **"Create repository"**

Setelah repo dibuat, upload file dengan salah satu cara:

**Cara A — Upload manual via browser:**
- Klik **"uploading an existing file"**
- Drag & drop semua file (`main.py`, `requirements.txt`, `.env.example`, `.gitignore`, `README.md`)
- Klik **"Commit changes"**

**Cara B — Via terminal:**
```bash
cd api_rekomendasi
git init
git add .
git commit -m "Initial commit: API Rekomendasi Keuangan"
git branch -M main
git remote add origin https://github.com/USERNAME/api-rekomendasi-keuangan.git
git push -u origin main
```
*(Ganti `USERNAME` dengan username GitHub kamu)*

---

### LANGKAH 3 — Deploy ke Railway (Gratis, dapat link HTTPS)

1. Buka [https://railway.app](https://railway.app) → Sign in with GitHub
2. Klik **"New Project"**
3. Pilih **"Deploy from GitHub repo"**
4. Pilih repo `api-rekomendasi-keuangan` yang baru kamu buat
5. Railway akan otomatis detect Python dan install requirements

**Set Environment Variable:**
6. Di dashboard Railway, klik project kamu → tab **"Variables"**
7. Klik **"New Variable"**
8. Isi:
   - Key: `GEMINI_API_KEY`
   - Value: (paste API key Gemini kamu)
9. Klik **"Add"**

**Set Start Command:**
10. Masuk ke tab **"Settings"** → bagian **"Deploy"**
11. Di "Start Command", isi:
    ```
    uvicorn main:app --host 0.0.0.0 --port $PORT
    ```
12. Klik **"Deploy"**

**Dapatkan Link:**
13. Setelah deploy selesai (1-2 menit), klik tab **"Settings"** → **"Domains"**
14. Klik **"Generate Domain"**
15. Kamu akan dapat link seperti: `https://api-rekomendasi-keuangan-production.up.railway.app`

✅ **API kamu sudah live!**

---

### ALTERNATIF — Deploy ke Render.com (juga gratis)

1. Buka [https://render.com](https://render.com) → Sign up with GitHub
2. Klik **"New"** → **"Web Service"**
3. Connect repo GitHub kamu
4. Isi:
   - Name: `api-rekomendasi-keuangan`
   - Runtime: **Python 3**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Di bagian **"Environment Variables"**, tambahkan `GEMINI_API_KEY`
6. Klik **"Create Web Service"**

---

## 📡 Cara Panggil API dari Frontend/Backend

### Endpoint 1: `/rekomendasi`

**Request (POST):**
```json
{
  "transaksi": [
    {"nama_produk": "indomie goreng", "kategori": "Makanan/Minuman", "total_pengeluaran": 3500},
    {"nama_produk": "token listrik", "kategori": "Tagihan/Utilitas", "total_pengeluaran": 100000},
    {"nama_produk": "nonton bioskop", "kategori": "Hiburan", "total_pengeluaran": 55000}
  ],
  "target_hemat": 500000,
  "gaya_hidup": "normal"
}
```

**Response:**
```json
{
  "status": "success",
  "rekomendasi": "## Analisis Transaksi Terbaru\n...",
  "ringkasan": {
    "total_pengeluaran": 158500,
    "jumlah_item": 3,
    "kategori": {"Tagihan/Utilitas": 100000, "Hiburan": 55000, "Makanan/Minuman": 3500}
  }
}
```

---

### Endpoint 2: `/chatbot`

**Request (POST):**
```json
{
  "pesan": "Bagaimana cara mengurangi pengeluaran hiburan saya?",
  "konteks_transaksi": [
    {"nama_produk": "nonton bioskop", "kategori": "Hiburan", "total_pengeluaran": 55000}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "jawaban": "Untuk mengurangi pengeluaran hiburan..."
}
```

---

### Contoh Fetch dari JavaScript (Frontend)

```javascript
const BASE_URL = "https://YOUR-APP.up.railway.app"; // ganti dengan URL kamu

// Panggil /rekomendasi
async function getRekomendasi(transaksi) {
  const response = await fetch(`${BASE_URL}/rekomendasi`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      transaksi: transaksi,
      target_hemat: 500000,
      gaya_hidup: "normal"
    })
  });
  const data = await response.json();
  return data.rekomendasi;
}

// Panggil /chatbot
async function tanyaAI(pesan) {
  const response = await fetch(`${BASE_URL}/chatbot`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pesan: pesan })
  });
  const data = await response.json();
  return data.jawaban;
}
```

---

### Contoh dari Python (Backend)

```python
import requests

BASE_URL = "https://YOUR-APP.up.railway.app"

# Rekomendasi
resp = requests.post(f"{BASE_URL}/rekomendasi", json={
    "transaksi": [
        {"nama_produk": "beras 5kg", "kategori": "Makanan/Minuman", "total_pengeluaran": 75000},
        {"nama_produk": "tagihan internet", "kategori": "Tagihan/Utilitas", "total_pengeluaran": 350000},
    ],
    "target_hemat": 500000,
    "gaya_hidup": "normal"
})
print(resp.json()["rekomendasi"])
```

---

## 🧪 Test Lokal (Opsional)

```bash
# Install dependensi
pip install -r requirements.txt

# Buat file .env
cp .env.example .env
# Edit .env, isi GEMINI_API_KEY

# Jalankan server
uvicorn main:app --reload

# Buka browser: http://localhost:8000/docs
```

---

## 🔗 Hubungkan ke Notebook Colab

Setelah API live, update Cell 13 di notebook kamu:

```python
import requests

API_URL = "https://YOUR-APP.up.railway.app"  # ← ganti URL

def test_api(transaksi):
    resp = requests.post(f"{API_URL}/rekomendasi", json={
        "transaksi": transaksi,
        "target_hemat": 500000,
        "gaya_hidup": "normal"
    })
    if resp.status_code == 200:
        print(resp.json()["rekomendasi"])
    else:
        print("Error:", resp.text)

test_api([
    {"nama_produk": "indomie", "kategori": "Makanan/Minuman", "total_pengeluaran": 3500},
    {"nama_produk": "token listrik", "kategori": "Tagihan/Utilitas", "total_pengeluaran": 100000},
])
```

---

*Powered by Google Gemini AI + FastAPI*
