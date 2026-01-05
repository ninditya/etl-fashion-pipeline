# =========================================
# SUBMISSION PROJECT: ETL PIPELINE PRODUK FASHION
# =========================================

# 1. Struktur dan Modularisasi Kode
Proyek ini mengikuti prinsip modularisasi:
- Setiap tahap ETL ditempatkan pada file masing-masing dalam folder utils/:
  * extract.py → mengambil data dari website.
  * transform.py → membersihkan dan menstandarisasi data mentah.
  * load.py → menyimpan data ke CSV, Google Sheets, dan PostgreSQL.
- Struktur folder lengkap:
SUBMISSION-PEMDA
├── utils/
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── tests/
│   ├── test_extract.py
│   ├── test_transform.py
│   └── test_load.py
├── google-sheets-api.json
├── main.py
├── products.csv
├── requirements.txt
└── submission.txt
File main.py menjadi entry point yang menjalankan pipeline secara berurutan: Extract → Transform → Load.

# 2. Extract (Web Scraping)
Sumber data: https://fashion-studio.dicoding.dev
- Semua halaman (1–50) di-scrap, menghasilkan ~1000 baris data mentah.
- Kolom hasil extract: Title, Price, Rating, Colors, Size, Gender.
- Timestamp ditambahkan untuk setiap baris data.
- Error handling dengan try-except agar proses tidak crash saat HTML rusak atau request gagal.
- Unit test extract mencakup semua skenario: HTML lengkap, field hilang, HTML rusak, dan request gagal.
- Coverage modul extract: 97%.

# 3. Transform (Data Cleaning & Standarisasi)
- Price: konversi dari $xxx ke rupiah (kurs Rp16.000), bertipe int.
- Rating: diubah menjadi float, bersih dari karakter tambahan.
- Colors: ambil angka saja.
- Size & Gender: string dibersihkan (misal, "Size: M" → "M").
- Hapus data buruk: null, duplikat, "Unknown Product".
- Tipe data kolom sesuai rubrik.
- Error handling untuk data tidak valid.
- Unit test mencakup:
  * Data normal → berhasil transform.
  * Data kosong → output tetap kosong.
  * Semua invalid → output kosong.
- Coverage modul transform: 90%.

# 4. Load (Repositori Data)
- Data bersih disimpan melalui load.py ke:
  * CSV → wajib (products.csv)
  * Google Sheets → wajib (service account .json, akses editor)
  * PostgreSQL → opsional
- Setiap fungsi load memiliki error handling:
  * DF kosong → print msg, tidak disimpan
  * DF berisi → simpan CSV/DB/GSheet
  * Exception → tertangani & dicetak
- Unit test mencakup semua cabang.
- Coverage modul load: 89%.

# 5. Unit Test & Coverage
- Semua modul diuji dengan unit test di folder tests/.
- Test mencakup extract, transform, load.
- Tidak ada test gagal.
- Coverage gabungan ETL: 92%, menjamin semua cabang logika utama diuji.

# 6. Menjalankan ETL Pipeline
Pastikan dependencies sudah terinstall dan up-to-date:

# Install dependencies proyek
pip install -r requirements.txt

# Jalankan pipeline ETL
python3 main.py

# 7. Menjalankan Unit Test
python3 -m pytest tests

# 8. Menjalankan Test Coverage
python3 -m pytest --cov=utils tests/ -v

# 9. URL Google Sheets
https://docs.google.com/spreadsheets/d/1nKOSdLbGnllou1yGTFGQAtgbFPhXWZ2cVsDv13R668U

# 10. Diagram Alur Gabungan ETL + Unit Test Coverage

                      ┌─────────────────────────────┐
                      │         EXTRACT            │
                      └─────────────┬───────────────┘
                                    │
                         ┌──────────┴──────────┐
                         │ Website response     │
                         └──────────┬──────────┘
                 ┌───────────────┴───────────────┐
                 │ Apakah HTML rusak / error?    │
                 ├───────────────┬───────────────┤
              Yes │               │ No            │
                 ▼               ▼
      extract_product() → None  extract_product() → dict
                 │               │
                 └───────────────┴───────────────┐
                                                 ▼
                                        DataFrame terisi?
                                        ├───────────┬───────────┤
                                     Yes │           │ No        │
                                         ▼           ▼
                                    TRANSFORM     DF kosong → stop
                                         │
                      ┌──────────────────┴──────────────────┐
                      │ Bersihkan invalid & convert tipe    │
                      └─────────────┬──────────────┬────────┘
                        Semua valid │ Ada invalid   │ Semua invalid
                        ▼          ▼               ▼
                 clean_data DF   clean_data DF   DF kosong → stop
                        │
                        ▼
                      LOAD
        ┌─────────────┴─────────────┐
        │ save_csv()                │
        │ save_postgres()           │
        │ save_gsheet()             │
        └─────────────┬─────────────┘
          Branch:
          - DF kosong → print msg, return
          - DF berisi → write CSV/DB/GSheet
          - Exception → tangani & print