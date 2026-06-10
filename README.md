# 🌿 Mayasih - Platform Pengelolaan Sampah & Daur Ulang Kampus

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.35.0%2B-FF4B4B.svg)](https://streamlit.io/)
[![SQLAlchemy](https://img.shields.io/badge/Database-SQLAlchemy%20%2F%20SQLite-red.svg)](https://www.sqlalchemy.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](#)

**Mayasih** (*Recycling for Campus*) adalah platform digital inovatif berbasis web yang dirancang khusus untuk civitas akademika **Universitas Mayasari Bakti**. Proyek ini dikembangkan sebagai **Tugas Besar (Tubes) Algoritma & Pemrograman**, dengan fokus pada otomatisasi pelaporan sampah, edukasi ramah lingkungan, dan sistem insentif (*reward*) berbasis poin untuk menciptakan lingkungan kampus yang hijau (*Green Campus*).

---

## 🎨 Sistem Desain & Estetika
Aplikasi ini mengadopsi **Tesla Design System & Minimalist MallSampah Aesthetic** dengan antarmuka yang modern, bersih, dan mewah:
- **Warna Utama**: Hijau Organik (`#1A9B4B`), Electric Blue (`#3E6AE1`), Carbon Dark (`#171A20`), dan Pure White (`#FFFFFF`).
- **Typografi**: Google Fonts **Inter** untuk keterbacaan tingkat tinggi.
- **Interaksi**: Efek melayang (*hover effect*), tombol navigasi absolut, serta transisi mulus (*smooth scrolling*).
- **Sidebar**: Desain kustom dengan tombol navigasi bertema biru cerah agar mudah dioperasikan.

---

## 🚀 Fitur Utama

### 👥 1. Peran Mahasiswa / Civitas Akademika (User)
*   **Registrasi & Login Berbasis NIM**: Masuk instan hanya dengan menggunakan Nomor Induk Mahasiswa (NIM). Sistem mendeteksi otomatis jika NIM belum terdaftar dan mengarahkan ke formulir registrasi singkat.
*   **Dashboard Interaktif**: Statistik poin terkini, jumlah laporan yang diajukan, tingkat keaktifan, dan pintasan cepat.
*   **Pelaporan Sampah (Laporan)**: Laporkan penumpukan sampah di area kampus dengan mengunggah foto, menentukan kategori sampah (Organik, Plastik, Kertas, Logam, B3), mendeskripsikan kondisi, dan menulis lokasi spesifik.
*   **Modul Edukasi & Kuis Poin**: Baca artikel edukasi lingkungan yang informatif dan jawab kuis terkait untuk mendapatkan poin tambahan secara langsung.
*   **Pencarian Artikel Wikipedia**: Fitur pencarian artikel Wikipedia (API Wikipedia Indonesia) terintegrasi untuk memperluas wawasan seputar ekologi, terhindar dari pemblokiran ISP.
*   **Penukaran Reward (Poin)**: Tukarkan poin yang terkumpul dengan voucher kantin, tumbler eksklusif, kaos ramah lingkungan, bibit tanaman, pulsa, dan lainnya.
*   **Leaderboard**: Papan peringkat waktu nyata yang menampilkan peringkat mahasiswa berdasarkan total poin yang dikumpulkan untuk memacu kompetisi positif.

### 🔐 2. Peran Pengelola Kampus (Admin)
*   **Dashboard Validasi Laporan**: Verifikasi laporan sampah dari mahasiswa. Admin dapat mengubah status laporan dari `Menunggu Verifikasi` $\rightarrow$ `Diproses` $\rightarrow$ `Selesai` dan secara otomatis memberikan poin apresiasi kepada pelapor.
*   **Manajemen Edukasi & Kuis**: Tambah, edit, atau hapus artikel edukasi serta pertanyaan kuis langsung melalui portal admin.
*   **Manajemen Reward**: Mengelola daftar hadiah, menyesuaikan tier (Tier 1-3), dan poin yang dibutuhkan untuk penukaran.
*   **Pengawasan Statistik Sistem**: Melihat data ringkasan aktivitas seluruh pengguna secara real-time.

---

## 📂 Struktur Direktori Proyek

```bash
Tubes Algoritma/
├── .streamlit/           # Konfigurasi Streamlit (tema dan tata letak)
├── instance/             # Folder database SQLite (mayasih.db)
├── static/               # Aset gambar statis
├── app.py                # Kode utama aplikasi (tampilan Streamlit & logika bisnis)
├── models.py             # Definisi skema database menggunakan SQLAlchemy ORM
├── seed.py               # Script seeding untuk mengisi data awal (mock data)
├── test_app.py           # Unit testing untuk fungsionalitas inti aplikasi
├── requirements.txt      # Daftar dependensi pustaka Python
└── README.md             # Dokumentasi proyek (file ini)
```

---

## 🛠️ Panduan Instalasi & Menjalankan Aplikasi

Ikuti langkah-langkah di bawah ini untuk menjalankan proyek Mayasih di lingkungan lokal Anda.

### 1. Prasyarat
Pastikan Anda sudah menginstal **Python 3.8** atau versi yang lebih baru di komputer Anda.

### 2. Kloning Proyek & Masuk ke Direktori
Buka terminal/command prompt, lalu masuk ke direktori proyek:
```bash
cd "C:\Users\muhda\Downloads\Tubes Algoritma"
```

### 3. Buat dan Aktifkan Virtual Environment (Direkomendasikan)
*   **Windows**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS/Linux**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 4. Instal Dependensi
Pasang semua pustaka yang dibutuhkan menggunakan `pip`:
```bash
pip install -r requirements.txt
```

### 5. Inisialisasi & Seed Database
Jalankan script `seed.py` untuk membuat tabel database dan mengisinya dengan data sampel (akun demo, kuis, artikel edukasi, dan contoh laporan):
```bash
python seed.py
```
*Database SQLite baru akan dibuat secara otomatis di dalam folder `instance/mayasih.db`.*

### 6. Jalankan Aplikasi Streamlit
Luncurkan server pengembangan Streamlit:
```bash
streamlit run app.py
```
Aplikasi akan otomatis terbuka di peramban web default Anda pada alamat `http://localhost:8501`.

---

## 🔑 Akun Demo Pengujian

Untuk mempermudah demonstrasi dan pengujian, berikut adalah beberapa kredensial akun yang siap digunakan setelah proses seeding:

| Peran | Kredensial Akses | Nama Pengguna | Catatan |
| :--- | :--- | :--- | :--- |
| **Admin** | Email: `admin@mayasih.id` <br> Password: `admin123` | Administrator Mayasih | Digunakan untuk menyetujui laporan sampah & mengelola edukasi/kuis |
| **Mahasiswa 1** | NIM: `1210001` | Ahmad Fauzi | Memiliki saldo awal **530 poin** |
| **Mahasiswa 2** | NIM: `1210002` | Laras Kirana | Memiliki saldo awal **490 poin** |
| **Mahasiswa 3** | NIM: `1210003` | Rian Hidayat | Memiliki saldo awal **130 poin** |

> 💡 *Anda juga dapat mencoba mendaftarkan **NIM baru** secara langsung pada halaman login mahasiswa.*

---

## 🧪 Pengujian Unit (Unit Testing)

Proyek ini dilengkapi dengan unit test otomatis untuk menjamin keandalan sistem pendaftaran/login NIM dan akurasi kalkulasi penambahan poin aktivitas.

Untuk menjalankan pengujian unit:
```bash
python -m unittest test_app.py
```

---

## 👥 Tim Pengembang (Kelompok Tubes)
*   **Universitas Mayasari Bakti**
*   Program Studi Ilmu Komputer / Teknik Informatika
*   Mata Kuliah: Algoritma & Pemrograman

---
🌿 *Mari bersama kita wujudkan kampus bebas sampah dan ramah lingkungan. **#ubahjadikebaikan**!*
