import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

# Ensure the instance directory exists for SQLite database
os.makedirs('instance', exist_ok=True)

DATABASE_URL = 'sqlite:///instance/mayasih.db'
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    nim = Column(String(20), unique=True, nullable=True)
    nama = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(200), nullable=True)
    total_poin = Column(Integer, default=0)
    role = Column(String(20), default='user') # 'user' or 'admin'

    # Relationships
    laporan = relationship('Laporan', back_populates='reporter', cascade="all, delete-orphan")
    penukaran = relationship('PenukaranReward', back_populates='user', cascade="all, delete-orphan")
    riwayat_poin = relationship('RiwayatPoin', back_populates='user', cascade="all, delete-orphan")
    aktivitas = relationship('Aktivitas', back_populates='user', cascade="all, delete-orphan")

class Edukasi(Base):
    __tablename__ = 'edukasi'
    id = Column(Integer, primary_key=True)
    judul = Column(String(200), nullable=False)
    isi = Column(Text, nullable=False)
    kategori = Column(String(50), nullable=False)
    tanggal = Column(DateTime, default=datetime.utcnow)

    # Relationships
    quizzes = relationship('Quiz', back_populates='edukasi', cascade="all, delete-orphan")

class Quiz(Base):
    __tablename__ = 'quiz'
    id = Column(Integer, primary_key=True)
    edukasi_id = Column(Integer, ForeignKey('edukasi.id'), nullable=False)
    pertanyaan = Column(String(500), nullable=False)
    pilihan_a = Column(String(200), nullable=False)
    pilihan_b = Column(String(200), nullable=False)
    pilihan_c = Column(String(200), nullable=False)
    pilihan_d = Column(String(200), nullable=False)
    jawaban_benar = Column(String(1), nullable=False) # 'A', 'B', 'C', 'D'

    # Relationships
    edukasi = relationship('Edukasi', back_populates='quizzes')

class Laporan(Base):
    __tablename__ = 'laporan'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    foto = Column(String(200), nullable=False)
    lokasi = Column(String(200), nullable=False)
    kategori_sampah = Column(String(50), nullable=False)
    deskripsi = Column(Text, nullable=False)
    status = Column(String(50), default='Menunggu Verifikasi') # 'Menunggu Verifikasi', 'Diproses', 'Selesai'
    tanggal = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reporter = relationship('User', back_populates='laporan')

class Reward(Base):
    __tablename__ = 'reward'
    id = Column(Integer, primary_key=True)
    nama_reward = Column(String(100), nullable=False)
    tier = Column(Integer, nullable=False) # 1, 2, 3
    poin_dibutuhkan = Column(Integer, nullable=False)

    # Relationships
    penukaran = relationship('PenukaranReward', back_populates='reward', cascade="all, delete-orphan")

class PenukaranReward(Base):
    __tablename__ = 'penukaran_reward'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reward_id = Column(Integer, ForeignKey('reward.id'), nullable=False)
    tanggal_penukaran = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='penukaran')
    reward = relationship('Reward', back_populates='penukaran')

class RiwayatPoin(Base):
    __tablename__ = 'riwayat_poin'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    aktivitas = Column(String(200), nullable=False)
    jumlah_poin = Column(Integer, nullable=False)
    tanggal = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='riwayat_poin')

class Aktivitas(Base):
    __tablename__ = 'aktivitas'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    aktivitas = Column(String(200), nullable=False)
    poin = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship('User', back_populates='aktivitas')

# Helper to create tables
def init_db():
    Base.metadata.create_all(bind=engine)

# Helper context manager for session handling
class DbSession:
    def __enter__(self):
        self.session = SessionLocal()
        return self.session
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.session.rollback()
        self.session.close()
