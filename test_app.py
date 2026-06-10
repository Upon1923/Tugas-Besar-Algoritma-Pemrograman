import unittest
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Edukasi, Quiz, Laporan, Reward, PenukaranReward, RiwayatPoin, Aktivitas
from app import add_user_points

class MayasihTestCase(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()
        
        # Seed test admin
        self.admin = User(
            nama="Test Admin",
            email="admin@mayasih.id",
            password="admin",
            role="admin"
        )
        self.session.add(self.admin)
        
        # Seed test article
        self.article = Edukasi(
            judul="Pengenalan Pemilahan Sampah",
            isi="Ini adalah materi pemilahan sampah organik dan anorganik.",
            kategori="Pemilahan Sampah"
        )
        self.session.add(self.article)
        self.session.commit()
        
        # Seed quiz question
        self.quiz = Quiz(
            edukasi_id=self.article.id,
            pertanyaan="Apakah sisa daun termasuk sampah organik?",
            pilihan_a="Ya",
            pilihan_b="Tidak",
            pilihan_c="Ragu-ragu",
            pilihan_d="Semua salah",
            jawaban_benar="A"
        )
        self.session.add(self.quiz)
        
        # Seed reward
        self.reward = Reward(
            nama_reward="Voucher Kantin Test",
            tier=1,
            poin_dibutuhkan=100
        )
        self.session.add(self.reward)
        self.session.commit()

    def tearDown(self):
        self.session.close()
        Base.metadata.drop_all(self.engine)

    def test_student_login_flow(self):
        # 1. Simulate new student detection and registration
        nim = '2210009'
        user = self.session.query(User).filter_by(nim=nim).first()
        self.assertIsNone(user) # Should not exist yet
        
        # Simulate registration
        new_student = User(
            nim=nim,
            nama='Budi Santoso',
            total_poin=0,
            role='user'
        )
        self.session.add(new_student)
        self.session.commit()
        
        # Verify in database
        db_user = self.session.query(User).filter_by(nim=nim).first()
        self.assertIsNotNone(db_user)
        self.assertEqual(db_user.nama, 'Budi Santoso')
        self.assertEqual(db_user.total_poin, 0)
        
        # 2. Simulate logging in with registered NIM
        registered_user = self.session.query(User).filter_by(nim=nim).first()
        self.assertIsNotNone(registered_user)
        self.assertEqual(registered_user.nama, 'Budi Santoso')

    def test_point_additions_on_read(self):
        # Create student
        student = User(
            nim='2210009',
            nama='Budi Santoso',
            total_poin=0,
            role='user'
        )
        self.session.add(student)
        self.session.commit()
        
        # Trigger point addition helper
        activity_name = f"Membaca materi: {self.article.judul}"
        add_user_points(self.session, student, 10, activity_name)
        
        # Verify student total points incremented
        self.assertEqual(student.total_poin, 10)
        
        # Verify RiwayatPoin and Aktivitas logs exist
        rp = self.session.query(RiwayatPoin).filter_by(user_id=student.id).first()
        self.assertIsNotNone(rp)
        self.assertEqual(rp.jumlah_poin, 10)
        self.assertEqual(rp.aktivitas, activity_name)
        
        ak = self.session.query(Aktivitas).filter_by(user_id=student.id).first()
        self.assertIsNotNone(ak)
        self.assertEqual(ak.poin, 10)
        self.assertEqual(ak.aktivitas, activity_name)

if __name__ == '__main__':
    unittest.main()
