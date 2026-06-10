import os
from werkzeug.security import generate_password_hash
from models import engine, SessionLocal, Base, User, Edukasi, Quiz, Laporan, Reward, PenukaranReward, RiwayatPoin, Aktivitas
from datetime import datetime, timedelta

def seed_database(drop_existing=True):
    print("Starting database seeding...")
    
    # 1. Clear existing database tables
    if drop_existing:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    try:
        # 2. Add Users (Admin and standard users)
        admin = User(
            nama="Administrator Mayasih",
            email="admin@mayasih.id",
            password=generate_password_hash("admin123"),
            role="admin",
            total_poin=0
        )
        
        student_1 = User(
            nim="1210001",
            nama="Ahmad Fauzi",
            total_poin=450,
            role="user"
        )
        
        student_2 = User(
            nim="1210002",
            nama="Laras Kirana",
            total_poin=1200,
            role="user"
        )
        
        student_3 = User(
            nim="1210003",
            nama="Rian Hidayat",
            total_poin=80,
            role="user"
        )
        
        session.add_all([admin, student_1, student_2, student_3])
        session.commit()
        
        # 3. Add Educational Materials
        ed1 = Edukasi(
            judul="Pedoman Dasar Pemilahan Sampah Kampus",
            isi="Pemilahan sampah di area kampus Universitas Mayasari Bakti dibagi menjadi tiga kategori utama: sampah organik, anorganik, dan sampah bahan berbahaya dan beracun (B3). Sampah organik mencakup sisa makanan dan dedaunan yang dapat diolah menjadi kompos. Sampah anorganik seperti botol plastik, kertas, dan kaleng logam dikumpulkan untuk didaur ulang. Sampah B3 seperti masker medis, baterai bekas, dan sisa bahan laboratorium harus dibuang secara terpisah agar tidak mencemari lingkungan kampus.",
            kategori="Pemilahan Sampah",
            tanggal=datetime.utcnow() - timedelta(days=5)
        )
        
        ed2 = Edukasi(
            judul="Dampak Buruk Plastik Sekali Pakai di Sekitar Kita",
            isi="Penggunaan kantong plastik sekali pakai, sedotan, dan botol minum plastik menyumbang lebih dari 60 persen volume timbunan sampah di area kampus. Plastik membutuhkan waktu ratusan tahun untuk terurai di alam dan dapat terpecah menjadi mikroplastik yang membahayakan rantai makanan. Dengan membawa botol minum (tumbler) dan kantong belanja sendiri ke kantin kampus, civitas akademika dapat memotong ribuan ton limbah plastik setiap tahunnya.",
            kategori="Sampah Plastik",
            tanggal=datetime.utcnow() - timedelta(days=4)
        )
        
        ed3 = Edukasi(
            judul="Daur Ulang Kertas Mandiri untuk Mahasiswa",
            isi="Tugas kuliah dan berkas administrasi seringkali menyisakan sampah kertas dalam jumlah besar. Kertas sebenarnya memiliki nilai daur ulang yang tinggi jika dipisahkan dari limbah basah. Kertas bekas yang bersih dapat diolah kembali menjadi kertas seni kreatif, pembatas buku, atau dikirim ke pengepul daur ulang kampus. Menghemat satu rim kertas setara dengan menyelamatkan satu pohon dewasa dari penebangan.",
            kategori="Daur Ulang",
            tanggal=datetime.utcnow() - timedelta(days=3)
        )
        
        ed4 = Edukasi(
            judul="Strategi Zero Waste Lifestyle di Lingkungan Kampus",
            isi="Gaya hidup Zero Waste (Nol Sampah) tidak berarti kita tidak menghasilkan sampah sama sekali, melainkan berupaya meminimalkan limbah yang dibuang ke Tempat Pembuangan Akhir (TPA). Strategi utama meliputi: Refuse (menolak barang sekali pakai), Reduce (mengurangi konsumsi), Reuse (menggunakan kembali), Recycle (mendaur ulang), dan Rot (mengompos sisa organik). Penerapan di kampus dapat dimulai dengan menolak sendok plastik sekali pakai saat membeli makanan.",
            kategori="Kampus Hijau",
            tanggal=datetime.utcnow() - timedelta(days=2)
        )
        
        session.add_all([ed1, ed2, ed3, ed4])
        session.commit()
        
        # 4. Add Quizzes for each educational material
        q1_1 = Quiz(
            edukasi_id=ed1.id,
            pertanyaan="Berdasarkan kategori pemilahan di kampus, manakah yang tergolong sampah organik?",
            pilihan_a="Botol plastik bekas air mineral",
            pilihan_b="Sisa makanan dari kantin dan dedaunan",
            pilihan_c="Baterai bekas dan masker medis",
            pilihan_d="Kertas pembungkus tugas kuliah",
            jawaban_benar="B"
        )
        q1_2 = Quiz(
            edukasi_id=ed1.id,
            pertanyaan="Mengapa sampah B3 seperti baterai bekas harus dipisahkan dari sampah lainnya?",
            pilihan_a="Karena memiliki nilai jual yang tinggi",
            pilihan_b="Karena baterai mudah membusuk dan mengeluarkan bau menyengat",
            pilihan_c="Karena mengandung bahan kimia berbahaya yang dapat mencemari tanah dan air",
            pilihan_d="Karena baterai bisa dilelehkan bersama botol plastik",
            jawaban_benar="C"
        )
        
        q2_1 = Quiz(
            edukasi_id=ed2.id,
            pertanyaan="Berapa persentase kontribusi plastik sekali pakai terhadap volume sampah kampus?",
            pilihan_a="Sekitar 10 persen",
            pilihan_b="Sekitar 30 persen",
            pilihan_c="Lebih dari 60 persen",
            pilihan_d="Kurang dari 5 persen",
            jawaban_benar="C"
        )
        q2_2 = Quiz(
            edukasi_id=ed2.id,
            pertanyaan="Apa tindakan paling efektif bagi mahasiswa untuk mengurangi timbunan sampah plastik di kantin?",
            pilihan_a="Meminta sendok plastik baru setiap kali makan",
            pilihan_b="Membawa tumbler dan kantong belanja sendiri dari rumah",
            pilihan_c="Membuang botol plastik langsung ke selokan kampus",
            pilihan_d="Menggunakan kantong plastik berlapis-lapis",
            jawaban_benar="B"
        )
        
        q3_1 = Quiz(
            edukasi_id=ed3.id,
            pertanyaan="Menghemat satu rim kertas cetak secara nyata setara dengan menyelamatkan...",
            pilihan_a="Satu pohon dewasa dari penebangan",
            pilihan_b="Sepuluh pohon kelapa sawit",
            pilihan_c="Seratus ekor burung langka",
            pilihan_d="Setengah hektar hutan lindung",
            jawaban_benar="A"
        )
        
        q4_1 = Quiz(
            edukasi_id=ed4.id,
            pertanyaan="Apakah yang dimaksud dengan 'Refuse' dalam prinsip dasar Zero Waste?",
            pilihan_a="Mendaur ulang seluruh barang plastik",
            pilihan_b="Menolak barang sekali pakai yang berpotensi menjadi sampah",
            pilihan_c="Mengurangi konsumsi makanan berkalori tinggi",
            pilihan_d="Mengubur sampah dalam lubang biopori",
            jawaban_benar="B"
        )
        
        session.add_all([q1_1, q1_2, q2_1, q2_2, q3_1, q4_1])
        session.commit()
        
        # 5. Add standard Rewards
        rewards = [
            Reward(nama_reward="Voucher Kantin Kampus Rp10.000", tier=1, poin_dibutuhkan=150),
            Reward(nama_reward="Voucher Kopi Diskon 50 Persen", tier=1, poin_dibutuhkan=200),
            Reward(nama_reward="Pulsa Seluler Rp5.000", tier=1, poin_dibutuhkan=300),
            Reward(nama_reward="Paket Kuota Internet 1GB", tier=1, poin_dibutuhkan=400),
            
            Reward(nama_reward="Tumbler Kaca Eksklusif Mayasih", tier=2, poin_dibutuhkan=600),
            Reward(nama_reward="Tote Bag Kanvas Kampanye Lingkungan", tier=2, poin_dibutuhkan=700),
            Reward(nama_reward="Buku Tulis Daur Ulang Kreatif", tier=2, poin_dibutuhkan=800),
            Reward(nama_reward="Bibit Tanaman Hias Hijau", tier=2, poin_dibutuhkan=1000),
            Reward(nama_reward="Kaos Katun Ramah Lingkungan", tier=2, poin_dibutuhkan=1200),
            
            Reward(nama_reward="Voucher Belanja Swalayan Rp100.000", tier=3, poin_dibutuhkan=1600),
            Reward(nama_reward="Voucher Transportasi Online Rp50.000", tier=3, poin_dibutuhkan=1800),
            Reward(nama_reward="Paket Sembako Kecil Universitas", tier=3, poin_dibutuhkan=2000),
            Reward(nama_reward="Tiket Masuk Seminar Lingkungan Nasional", tier=3, poin_dibutuhkan=2500),
        ]
        
        for r in rewards:
            session.add(r)
        session.commit()
        
        # 6. Add Mock Reports
        reports = [
            Laporan(
                user_id=student_1.id,
                foto="sampah_koridor.jpg",
                lokasi="Koridor Lantai 2 Gedung Fasilkom",
                kategori_sampah="Kertas",
                deskripsi="Ada tumpukan kertas bekas tugas dan kardus pembungkus yang berserakan di pojok dekat toilet laki-laki, mengganggu jalan masuk koridor.",
                status="Selesai",
                tanggal=datetime.utcnow() - timedelta(days=4)
            ),
            Laporan(
                user_id=student_2.id,
                foto="sampah_kantin.jpg",
                lokasi="Area Taman Belakang Kantin Pusat",
                kategori_sampah="Plastik",
                deskripsi="Banyak botol plastik dan sedotan bekas berserakan di bawah bangku semen taman belakang kantin. Petugas pembersih belum membersihkan area ini.",
                status="Diproses",
                tanggal=datetime.utcnow() - timedelta(days=2)
            ),
            Laporan(
                user_id=student_2.id,
                foto="sampah_parkir.jpg",
                lokasi="Area Parkir Sepeda Motor Gerbang Barat",
                kategori_sampah="Logam",
                deskripsi="Ada kaleng minuman soda berkarat dan beberapa kawat besi tajam yang tertinggal di dekat pembatas parkir motor. Berbahaya jika mengenai ban kendaraan.",
                status="Menunggu Verifikasi",
                tanggal=datetime.utcnow() - timedelta(hours=5)
            ),
            Laporan(
                user_id=student_3.id,
                foto="sampah_organik.jpg",
                lokasi="Halaman Depan Perpustakaan Utama",
                kategori_sampah="Organik",
                deskripsi="Timbunan daun kering akibat pemangkasan pohon menutupi sebagian jalur pedestrian dan belum diangkat ke tempat pembuangan sampah akhir.",
                status="Menunggu Verifikasi",
                tanggal=datetime.utcnow() - timedelta(hours=2)
            )
        ]
        
        for rep in reports:
            session.add(rep)
        session.commit()
        
        # 7. Seed RiwayatPoin and Aktivitas
        logs = [
            (student_1, "Membaca materi: Pedoman Dasar Pemilahan Sampah Kampus", 10, datetime.utcnow() - timedelta(days=5)),
            (student_1, "Menyelesaikan quiz: Pedoman Dasar Pemilahan Sampah Kampus", 20, datetime.utcnow() - timedelta(days=5)),
            (student_1, "Mengirim laporan: Koridor Lantai 2 Gedung Fasilkom", 100, datetime.utcnow() - timedelta(days=4)),
            (student_1, "Laporan diverifikasi: Koridor Lantai 2 Gedung Fasilkom", 150, datetime.utcnow() - timedelta(days=4)),
            (student_1, "Mengikuti aksi bersih kampus: Lingkungan Rektorat", 250, datetime.utcnow() - timedelta(days=3)),
            
            (student_2, "Membaca materi: Dampak Buruk Plastik Sekali Pakai", 10, datetime.utcnow() - timedelta(days=4)),
            (student_2, "Menyelesaikan quiz: Dampak Buruk Plastik Sekali Pakai", 20, datetime.utcnow() - timedelta(days=4)),
            (student_2, "Membaca materi: Daur Ulang Kertas Mandiri", 10, datetime.utcnow() - timedelta(days=3)),
            (student_2, "Mengirim laporan: Area Taman Belakang Kantin Pusat", 100, datetime.utcnow() - timedelta(days=2)),
            (student_2, "Mengirim laporan: Area Parkir Sepeda Motor Gerbang Barat", 100, datetime.utcnow() - timedelta(hours=5)),
            (student_2, "Mengikuti aksi bersih kampus: Pantai Kemitraan Kampus", 250, datetime.utcnow() - timedelta(days=1)),
            
            (student_3, "Membaca materi: Strategi Zero Waste Lifestyle", 10, datetime.utcnow() - timedelta(days=2)),
            (student_3, "Menyelesaikan quiz: Strategi Zero Waste Lifestyle", 20, datetime.utcnow() - timedelta(days=2)),
            (student_3, "Mengirim laporan: Halaman Depan Perpustakaan Utama", 100, datetime.utcnow() - timedelta(hours=2)),
        ]
        
        for u, act, pt, dt in logs:
            rp = RiwayatPoin(user_id=u.id, aktivitas=act, jumlah_poin=pt, tanggal=dt)
            ak = Aktivitas(user_id=u.id, aktivitas=act, poin=pt, created_at=dt)
            session.add(rp)
            session.add(ak)
            
        session.commit()
        
        # Adjust total points to match
        student_1.total_poin = 530
        student_2.total_poin = 490
        student_3.total_poin = 130
        session.commit()
        
        print("Database successfully seeded with standard datasets.")
    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    seed_database(drop_existing=True)
