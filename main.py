"""
API Rekomendasi Keuangan — Powered by Google Gemini AI
Endpoints:
  POST /rekomendasi   — Kirim transaksi, dapat rekomendasi AI
  POST /chatbot       — Tanya jawab bebas tentang keuangan
  GET  /health        — Cek status server
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List
import google.generativeai as genai
import os

# ─── Setup ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="API Rekomendasi Keuangan",
    description="Sistem rekomendasi pengeluaran berbasis Google Gemini AI",
    version="1.0.0"
)

# CORS — izinkan semua origin (sesuaikan untuk production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ambil API key dari environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel("models/gemini-2.5-flash")
else:
    model = None  # Akan error saat dipanggil jika tidak ada key


# ─── Schema ──────────────────────────────────────────────────────────────────
class ItemTransaksi(BaseModel):
    nama_produk: str = Field(..., example="indomie goreng")
    kategori: str = Field(..., example="Makanan/Minuman")
    total_pengeluaran: float = Field(..., example=3500)

class RiwayatBulan(BaseModel):
    bulan: str = Field(..., example="2024-10")
    total: float = Field(..., example=1500000)
    kategori_terbesar: str = Field(..., example="Makanan/Minuman")

class RekomendasiRequest(BaseModel):
    transaksi: List[ItemTransaksi] = Field(..., min_length=1)
    riwayat_bulanan: Optional[List[RiwayatBulan]] = None
    target_hemat: Optional[float] = Field(None, example=500000)
    gaya_hidup: Optional[str] = Field("normal", example="hemat / normal / konsumtif")

class ChatRequest(BaseModel):
    pesan: str = Field(..., example="Bagaimana cara mengurangi pengeluaran makanan?")
    konteks_transaksi: Optional[List[ItemTransaksi]] = None


# ─── Helper ──────────────────────────────────────────────────────────────────
def rupiah(angka: float) -> str:
    try:
        return f"Rp {angka:,.0f}".replace(",", ".")
    except Exception:
        return "Rp 0"


def build_prompt(req: RekomendasiRequest) -> str:
    transaksi = req.transaksi
    total = sum(t.total_pengeluaran for t in transaksi)

    # Ringkasan kategori
    kat_map: dict[str, float] = {}
    for t in transaksi:
        kat_map[t.kategori] = kat_map.get(t.kategori, 0) + t.total_pengeluaran
    kat_sorted = sorted(kat_map.items(), key=lambda x: -x[1])

    detail_items = "\n".join(
        f"- {t.nama_produk} ({t.kategori}) → {rupiah(t.total_pengeluaran)}"
        for t in transaksi
    )
    ringkasan_kat = "\n".join(
        f"- {k}: {rupiah(v)} ({v/total*100:.1f}%)" for k, v in kat_sorted
    )

    riwayat_str = ""
    if req.riwayat_bulanan:
        riwayat_str = "RIWAYAT BULANAN:\n" + "\n".join(
            f"- {r.bulan}: {rupiah(r.total)} (terbesar: {r.kategori_terbesar})"
            for r in req.riwayat_bulanan
        )

    target_str = (
        f"Target penghematan: {rupiah(req.target_hemat)} per bulan"
        if req.target_hemat
        else "Belum ada target penghematan khusus"
    )

    return f"""Kamu adalah financial advisor profesional. Gunakan Bahasa Indonesia yang profesional, ringkas, dan actionable.

PENTING:
- Tanpa salam pembuka
- Tanpa menyebut nama orang atau pihak manapun
- Maksimal 100 kata total
- Hanya 3 rekomendasi singkat
- Format: bullet points pendek, langsung ke angka dan aksi nyata
- Tidak perlu kesimpulan atau penutup

PROFIL PENGGUNA
- Gaya hidup: {req.gaya_hidup}
- {target_str}

{riwayat_str}

RINGKASAN TRANSAKSI
- Total pengeluaran  : {rupiah(total)}
- Jumlah item        : {len(transaksi)}
- Rata-rata per item : {rupiah(total / len(transaksi))}
- Kategori terbesar  : {kat_sorted[0][0]} ({rupiah(kat_sorted[0][1])})

RINGKASAN KATEGORI
{ringkasan_kat}

DETAIL ITEM
{detail_items}

Gunakan format:
## Potensi Pemborosan
## 3 Rekomendasi Penghematan
## Strategi Belanja Berikutnya
## Target Bulan Depan
"""


# ─── Endpoints ───────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "gemini_configured": model is not None,
        "version": "1.0.0"
    }


@app.post("/rekomendasi")
def rekomendasi(req: RekomendasiRequest):
    """
    Kirim daftar transaksi, dapatkan analisis & rekomendasi keuangan dari Gemini AI.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY belum dikonfigurasi di server.")

    prompt = build_prompt(req)

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.6,
                max_output_tokens=4000,
                top_p=0.9,
                top_k=40,
            ),
        )
        hasil = ""
        try:
            if hasattr(response, "candidates"):
                for c in response.candidates:
                    if hasattr(c, "content"):
                        for p in c.content.parts:
                            if hasattr(p, "text"):
                                hasil += p.text
            if not hasil.strip():
                hasil = response.text
        except Exception:
            hasil = str(response)

        if not hasil.strip():
            raise HTTPException(status_code=502, detail="Gemini tidak mengembalikan respons.")

        total = sum(t.total_pengeluaran for t in req.transaksi)
        kat_map: dict[str, float] = {}
        for t in req.transaksi:
            kat_map[t.kategori] = kat_map.get(t.kategori, 0) + t.total_pengeluaran

        return {
            "status": "success",
            "rekomendasi": hasil.strip(),
            "ringkasan": {
                "total_pengeluaran": total,
                "jumlah_item": len(req.transaksi),
                "kategori": {k: v for k, v in sorted(kat_map.items(), key=lambda x: -x[1])},
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Gemini: {str(e)}")


@app.post("/chatbot")
def chatbot(req: ChatRequest):
    """
    Tanya jawab bebas tentang keuangan. Opsional: sertakan konteks transaksi.
    """
    if model is None:
        raise HTTPException(status_code=500, detail="GEMINI_API_KEY belum dikonfigurasi di server.")

    konteks_str = ""
    if req.konteks_transaksi:
        konteks_str = "Konteks transaksi pengguna:\n" + "\n".join(
            f"- {t.nama_produk} ({t.kategori}): {rupiah(t.total_pengeluaran)}"
            for t in req.konteks_transaksi
        )

    prompt = f"""Kamu adalah financial advisor yang ramah dan profesional.
Jawab dalam Bahasa Indonesia. Ringkas dan actionable.

{konteks_str}

Pertanyaan pengguna: {req.pesan}"""

    try:
        response = model.generate_content(prompt)
        jawaban = response.text.strip()
        return {"status": "success", "jawaban": jawaban}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error Gemini: {str(e)}")
