# -*- coding: utf-8 -*-
import os
import time
import base64
from datetime import datetime
import streamlit as st
import requests
import textwrap
from bs4 import BeautifulSoup
from PIL import Image
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func

# --- FUNGSI BANTUAN UNTUK MEMPERBAIKI STREAMLIT (TUGAS BESAR) ---
# Kami menyimpan fungsi bawaan Streamlit agar bisa dipanggil kembali
original_markdown = st.markdown
original_rerun = st.rerun

# Fungsi kustom agar format HTML di dalam python tidak rusak/berantakan
def custom_markdown(body="", *args, **kwargs):
    import textwrap
    if isinstance(body, str):
        # Hapus indentasi spasi di awal paragraf multiline
        body = textwrap.dedent(body)
        # Hapus spasi di setiap baris jika ada tag HTML
        if kwargs.get('unsafe_allow_html', False):
            body = '\n'.join(line.lstrip() for line in body.splitlines())
    return original_markdown(body, *args, **kwargs)

# Fungsi kustom agar database session otomatis tertutup setiap kali halaman refresh
def custom_rerun(*args, **kwargs):
    if 'db_session' in globals():
        try:
            globals()['db_session'].close()
        except:
            pass
    return original_rerun(*args, **kwargs)

# Ganti fungsi bawaan Streamlit dengan versi kustom kelompok kami
st.markdown = custom_markdown
st.rerun = custom_rerun


# Import our standard SQLAlchemy models and session helper
from models import (
    SessionLocal, User, Edukasi, Quiz, Laporan, Reward, 
    PenukaranReward, RiwayatPoin, Aktivitas, init_db
)

# Page Configuration
st.set_page_config(
    page_title="Mayasih - Universitas Mayasari Bakti",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database schema
init_db()

# Seed database if empty
session = SessionLocal()
if session.query(Reward).count() == 0 or session.query(Edukasi).count() == 0:
    try:
        from seed import seed_database
        seed_database(drop_existing=False)
    except Exception as e:
        st.warning(f"Error seeding database: {e}")
session.close()

# Helper to encode images for HTML rendering - cached to avoid lag on rerun and scrolling
@st.cache_data
def get_base64_image(image_path, mtime=0):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            data = f.read()
        return base64.b64encode(data).decode()
    return ""

def load_image(image_name):
    """Loads image and returns its data URI (with correct MIME type and modification time to bypass cache)."""
    if not image_name:
        return ""
        
    path = None
    if "." in image_name:
        if os.path.exists(image_name):
            path = image_name
    else:
        for ext in [".png", ".jpg", ".jpeg", ".PNG", ".JPG", ".JPEG"]:
            test_path = image_name + ext
            if os.path.exists(test_path):
                path = test_path
                break
                
    if path and os.path.exists(path):
        mtime = os.path.getmtime(path)
        b64_data = get_base64_image(path, mtime)
        if b64_data:
            ext = os.path.splitext(path)[1].lower()
            mime_type = "image/png"
            if ext in [".jpg", ".jpeg"]:
                mime_type = "image/jpeg"
            return f"data:{mime_type};base64,{b64_data}"
            
    return ""

# Custom CSS - Tesla Design System (Pure White, Electric Blue #3E6AE1, Carbon Dark #171A20)
st.markdown("""
<style>
    /* ===================================================
       TESLA DESIGN SYSTEM - Mayasih App
       Color Palette:
         Electric Blue:  #3E6AE1  (primary CTA only)
         Carbon Dark:    #171A20  (headings, nav)
         Graphite:       #393C41  (body text)
         Pewter:         #5C5E62  (tertiary text)
         Silver Fog:     #8E8E8E  (placeholder)
         Cloud Gray:     #EEEEEE  (borders/dividers)
         Light Ash:      #F4F4F4  (alternate surface)
         Pure White:     #FFFFFF  (canvas / surfaces)
    =================================================== */

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

    /* --- Global Reset & Canvas --- */
    .stApp {
        background-color: #FFFFFF !important;
        color: #393C41 !important;
        font-family: 'Inter', -apple-system, Arial, sans-serif !important;
        font-weight: 400 !important;
        font-size: 14px !important;
    }

    /* Keep Streamlit header transparent for sidebar toggle but hide menu and footer */
    #MainMenu {visibility: hidden; display: none !important;}
    footer {visibility: hidden; display: none !important;}
    [data-testid="stHeader"], .stAppHeader {
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stHeader"]::before, .stAppHeader::before {
        display: none !important;
    }

    /* Sidebar Collapse & Expand Toggle Buttons Styling - Bright Blue Theme */
    button[data-testid="stSidebarCollapse"],
    button[aria-label="Collapse sidebar"],
    button[aria-label="Expand sidebar"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"],
    .stAppHeader button[data-testid="stSidebarCollapse"],
    .stAppHeader button[aria-label="Expand sidebar"],
    .stAppHeader button[aria-label="Open sidebar"] {
        background-color: #0066cc !important; /* Bright Blue */
        color: #FFFFFF !important; /* White Chevron */
        border: 2px solid #0052a3 !important;
        border-radius: 8px !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        z-index: 999999 !important; /* Ensure it stays on top */
    }
    button[data-testid="stSidebarCollapse"]:hover,
    button[aria-label="Collapse sidebar"]:hover,
    button[aria-label="Expand sidebar"]:hover,
    button[aria-label="Open sidebar"]:hover,
    button[aria-label="Close sidebar"]:hover,
    .stAppHeader button[data-testid="stSidebarCollapse"]:hover,
    .stAppHeader button[aria-label="Expand sidebar"]:hover,
    .stAppHeader button[aria-label="Open sidebar"]:hover {
        background-color: #0052a3 !important; /* Darker Blue on Hover */
        border-color: #004080 !important;
        box-shadow: 0 6px 16px rgba(0, 82, 163, 0.4) !important;
    }
    button[data-testid="stSidebarCollapse"] svg,
    button[aria-label="Collapse sidebar"] svg,
    button[aria-label="Expand sidebar"] svg,
    button[aria-label="Open sidebar"] svg,
    button[aria-label="Close sidebar"] svg,
    .stAppHeader button[data-testid="stSidebarCollapse"] svg,
    .stAppHeader button[aria-label="Expand sidebar"] svg,
    .stAppHeader button[aria-label="Open sidebar"] svg {
        width: 28px !important;
        height: 28px !important;
        fill: #FFFFFF !important;
        color: #FFFFFF !important;
    }

    /* Full-bleed container - no side/vertical padding ceiling for hero */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }

    /* --- Headings --- */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', -apple-system, Arial, sans-serif !important;
        color: #171A20 !important;
        font-weight: 500 !important;
        letter-spacing: normal !important;
    }

    /* --- Sidebar --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EEEEEE !important;
        font-family: 'Inter', -apple-system, Arial, sans-serif !important;
    }
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] select,
    [data-testid="stSidebar"] input,
    [data-testid="stSidebar"] textarea {
        font-family: 'Inter', -apple-system, Arial, sans-serif !important;
    }

    /* Sidebar secondary nav buttons */
    div[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"] {
        background-color: transparent !important;
        color: #393C41 !important;
        border: none !important;
        border-radius: 4px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        transition: background-color 0.33s, color 0.33s !important;
        padding: 8px 16px !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }
    div[data-testid="stSidebar"] button[data-testid="stBaseButton-secondary"]:hover {
        background-color: #F4F4F4 !important;
        color: #171A20 !important;
    }

    /* Sidebar primary (active) nav buttons */
    div[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] {
        background-color: #171A20 !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 4px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        padding: 8px 16px !important;
        box-shadow: none !important;
        transition: background-color 0.33s !important;
    }
    div[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover {
        background-color: #393C41 !important;
    }

    /* --- User profile badge in sidebar --- */
    .user-badge {
        padding: 16px !important;
        background-color: #F4F4F4 !important;
        border: none !important;
        border-radius: 4px !important;
        margin-bottom: 16px !important;
    }

    /* --- Tesla Cards - flat, no shadow, Light Ash bg --- */
    .tesla-card {
        background-color: #F4F4F4 !important;
        border: none !important;
        padding: 28px !important;
        border-radius: 4px !important;
        margin-bottom: 16px;
        transition: background-color 0.33s !important;
    }
    .tesla-card:hover {
        background-color: #EEEEEE !important;
    }

    /* Keep old brutalist-card class mapped to tesla style for compatibility */
    .brutalist-card {
        background-color: #F4F4F4 !important;
        border: none !important;
        padding: 28px !important;
        border-radius: 4px !important;
        margin-bottom: 16px;
        box-shadow: none !important;
        transition: background-color 0.33s !important;
    }
    .brutalist-card:hover {
        background-color: #EEEEEE !important;
        transform: none !important;
        box-shadow: none !important;
    }

    /* --- Global Streamlit Buttons → Tesla style --- */
    .stButton > button {
        background-color: #3E6AE1 !important;
        color: #FFFFFF !important;
        border: 3px solid transparent !important;
        border-radius: 4px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        min-height: 40px !important;
        transition: background-color 0.33s, border-color 0.33s, box-shadow 0.25s !important;
        box-shadow: none !important;
        letter-spacing: normal !important;
    }
    .stButton > button:hover {
        background-color: #2e58c5 !important;
        transform: none !important;
        box-shadow: none !important;
    }
    /* Secondary button variant */
    .stButton > button[kind="secondary"],
    div button[data-testid="stBaseButton-secondary"]:not([data-testid*="stSidebar"] *) {
        background-color: #FFFFFF !important;
        color: #393C41 !important;
        border: 3px solid transparent !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background-color: #F4F4F4 !important;
    }

    /* --- Input Fields --- */
    div[data-testid="stTextInput"] input,
    div[data-testid="stTextArea"] textarea,
    div[data-testid="stSelectbox"] select {
        border-radius: 4px !important;
        border: 1px solid #D0D1D2 !important;
        background-color: #FFFFFF !important;
        color: #171A20 !important;
        padding: 8px 12px !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        transition: border-color 0.33s !important;
    }
    div[data-testid="stTextInput"] input:focus,
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #3E6AE1 !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input::placeholder,
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #8E8E8E !important;
    }

    /* --- Tab Bar --- */
    div[data-testid="stTabBar"] {
        background-color: transparent !important;
        border-bottom: 1px solid #EEEEEE !important;
        margin-bottom: 24px !important;
    }
    div[data-testid="stTabBar"] button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        color: #5C5E62 !important;
        background-color: transparent !important;
        border: none !important;
        padding: 8px 16px !important;
        transition: color 0.33s !important;
    }
    div[data-testid="stTabBar"] button[aria-selected="true"] {
        color: #171A20 !important;
        border-bottom: 2px solid #171A20 !important;
    }

    /* --- Tables --- */
    .stTable table {
        border-collapse: collapse !important;
        width: 100% !important;
        background-color: #FFFFFF !important;
        border-radius: 0 !important;
        border: none !important;
    }
    .stTable th {
        background-color: #F4F4F4 !important;
        color: #171A20 !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        text-align: left !important;
        padding: 12px 16px !important;
        border-bottom: 1px solid #EEEEEE !important;
        font-size: 14px !important;
    }
    .stTable td {
        padding: 12px 16px !important;
        border-bottom: 1px solid #EEEEEE !important;
        font-family: 'Inter', sans-serif !important;
        color: #393C41 !important;
        font-size: 14px !important;
    }

    /* --- Progress Bar --- */
    div[data-testid="stProgress"] > div {
        background-color: #EEEEEE !important;
        border-radius: 0 !important;
        height: 4px !important;
    }
    div[data-testid="stProgress"] > div > div {
        background-color: #3E6AE1 !important;
        border-radius: 0 !important;
    }

    /* --- Quiz Box - left border accent in blue --- */
    .quiz-box {
        background-color: #FFFFFF;
        border-left: 3px solid #3E6AE1;
        padding: 16px 20px;
        margin-bottom: 16px;
        border-radius: 0;
    }

    /* --- Images --- */
    div[data-testid="stImage"] img {
        border-radius: 12px !important;
        border: none !important;
        box-shadow: none !important;
    }

    /* --- Divider --- */
    hr {
        border: none !important;
        border-top: 1px solid #EEEEEE !important;
        margin: 24px 0 !important;
    }

    /* Activity row items */
    .activity-row {
        padding: 12px 0;
        border-bottom: 1px solid #EEEEEE;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
    }

    /* Leaderboard row */
    .lb-row {
        padding: 16px 24px;
        border-bottom: 1px solid #EEEEEE;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 14px;
        transition: background-color 0.33s;
    }
    .lb-row:hover {
        background-color: #F4F4F4;
    }
    .lb-row.first {
        background-color: #171A20;
        color: #FFFFFF;
        border: none;
    }
</style>
""", unsafe_allow_html=True)




# Helper functions
def add_user_points(session, user, amount, activity_name):
    """Adds points to user and records logs."""
    user.total_poin += amount
    
    # Save to RiwayatPoin
    rp = RiwayatPoin(
        user_id=user.id,
        aktivitas=activity_name,
        jumlah_poin=amount,
        tanggal=datetime.utcnow()
    )
    
    # Save to Aktivitas
    ak = Aktivitas(
        user_id=user.id,
        aktivitas=activity_name,
        poin=amount,
        created_at=datetime.utcnow()
    )
    
    session.add(rp)
    session.add(ak)
    session.commit()

def search_web_articles(query):
    """Searches Wikipedia API for environmental and waste management articles, avoiding ISP blocks."""
    import re
    results = []
    
    try:
        # Request search results from Indonesian Wikipedia
        full_query = f"sampah {query}"
        url = f"https://id.wikipedia.org/w/api.php?action=query&list=search&srsearch={requests.utils.quote(full_query)}&format=json"
        headers = {
            "User-Agent": "MayasihEducationApp/1.0 (admin@mayasih.id)"
        }
        r = requests.get(url, headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            search_items = data.get('query', {}).get('search', [])
            for item in search_items[:5]:
                title = item['title']
                snippet_raw = item['snippet']
                
                # Clean up HTML tags (like <span class="searchmatch">) from snippet
                snippet = re.sub(r'<[^>]+>', '', snippet_raw)
                snippet = snippet.replace('&quot;', '"').strip()
                if not snippet:
                    snippet = "Informasi artikel tidak tersedia."
                
                link = f"https://id.wikipedia.org/wiki/{requests.utils.quote(title.replace(' ', '_'))}"
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet + "..."
                })
    except Exception as e:
        print(f"Error searching Wikipedia: {e}")
        
    # High-quality fallbacks in case of network issues so the UI never displays empty results
    if not results:
        fallbacks = [
            {
                "title": f"Panduan Praktis Pengelolaan {query.capitalize()}",
                "link": "https://id.wikipedia.org/wiki/Daur_ulang",
                "snippet": f"Pelajari langkah mudah memilah dan mendaur ulang materi {query} di lingkungan sekitar kita untuk masa depan kampus yang lebih bersih."
            },
            {
                "title": f"Dampak Limbah {query.capitalize()} Terhadap Ekosistem",
                "link": "https://id.wikipedia.org/wiki/Pencemaran",
                "snippet": f"Penelitian mendalam tentang bagaimana limbah {query} yang tidak terkelola dengan baik merusak ekosistem tanah dan air di pemukiman sekitar."
            },
            {
                "title": "Prinsip Zero Waste di Lingkungan Universitas",
                "link": "https://id.wikipedia.org/wiki/Nir-sampah",
                "snippet": "Menerapkan gaya hidup bebas sampah dengan 5R (Refuse, Reduce, Reuse, Recycle, Rot) secara berkelanjutan di kalangan mahasiswa."
            }
        ]
        results = fallbacks
        
    return results


# Session State Initialization
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'role' not in st.session_state:
    st.session_state.role = None
if 'page' not in st.session_state:
    st.session_state.page = "Dashboard"
if 'register_mode' not in st.session_state:
    st.session_state.register_mode = False
if 'temp_nim' not in st.session_state:
    st.session_state.temp_nim = None
if 'quiz_start_time' not in st.session_state:
    st.session_state.quiz_start_time = None
if 'active_quiz_id' not in st.session_state:
    st.session_state.active_quiz_id = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = False
if 'login_role' not in st.session_state:
    st.session_state.login_role = 'user'

# Connect database session
db_session = SessionLocal()

# ----------------- LOGIN / REGISTER PAGE (LANDING PAGE) -----------------
if st.session_state.user_id is None:
    if not st.session_state.show_login:

        # Preload images
        hero_b64     = load_image("mayasih_hero_bg")
        waste_b64    = load_image("mahasiswa") or load_image("mayasih_feature_waste")
        rewards_b64  = load_image("mayasih_rewards_feature")
        sorting_b64  = load_image("sorting_waste")
        dosen_b64    = load_image("dosen") or load_image("mayasih_feature_dosen")
        kampus_b64   = load_image("kampus") or load_image("mayasih_feature_kampus")

        # ══════════════════════════════════════════
        # MALLSAMPAH-STYLE LANDING PAGE FOR CAMPUS
        # ══════════════════════════════════════════

        # Inject MallSampah-inspired green CSS overrides for landing page
        st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* MallSampah-inspired green palette */
    :root {
        --ms-green:      #1A9B4B;
        --ms-green-dark: #157A3C;
        --ms-green-light:#E8F5EE;
        --ms-green-bg:   #F0FAF4;
        --ms-text:       #1A1A1A;
        --ms-text-sub:   #555555;
        --ms-border:     #E0E0E0;
        --ms-white:      #FFFFFF;
    }

    /* Landing page nav - white with green accent */
    .ms-nav {
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255,255,255,0.96);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid #E8F0EC;
        padding: 0 60px;
        height: 64px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-family: 'Inter', Arial, sans-serif;
    }
    .ms-nav-logo {
        font-size: 22px;
        font-weight: 800;
        color: var(--ms-green);
        letter-spacing: -0.5px;
    }
    .ms-nav-links {
        display: flex;
        gap: 4px;
        align-items: center;
    }
    .ms-nav-link {
        font-size: 14px;
        font-weight: 500;
        color: #333;
        padding: 6px 18px;
        border-radius: 6px;
        cursor: pointer;
        transition: color 0.2s, background-color 0.2s;
    }
    .ms-nav-link:hover { color: var(--ms-green); background: var(--ms-green-light); }

    /* Hero */
    .ms-hero {
        position: relative;
        min-height: 88vh;
        display: flex;
        align-items: center;
        overflow: hidden;
        background: var(--ms-green);
        margin: 0 -1rem;
    }
    .ms-hero-overlay {
        position: absolute; inset: 0;
        background: linear-gradient(105deg, rgba(20,100,55,0.92) 0%, rgba(20,100,55,0.5) 55%, rgba(20,100,55,0.1) 100%);
        z-index: 1;
    }
    .ms-hero-content {
        position: relative;
        z-index: 2;
        padding: 0 80px;
        max-width: 600px;
    }
    .ms-hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        color: #fff;
        font-size: 13px;
        font-weight: 600;
        padding: 6px 16px;
        border-radius: 100px;
        margin-bottom: 24px;
        letter-spacing: 0.5px;
        border: 1px solid rgba(255,255,255,0.3);
    }
    .ms-hero h1 {
        font-family: 'Inter', Arial, sans-serif !important;
        font-size: 56px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        line-height: 1.1 !important;
        margin: 0 0 16px 0 !important;
        letter-spacing: -1px !important;
    }
    .ms-hero-sub {
        font-size: 18px;
        color: rgba(255,255,255,0.88);
        line-height: 1.6;
        margin-bottom: 12px;
        font-weight: 400;
    }
    .ms-hero-hashtag {
        font-size: 15px;
        color: rgba(255,255,255,0.7);
        font-weight: 500;
        margin-bottom: 40px;
    }
    .ms-hero-dots {
        position: absolute;
        left: 24px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 3;
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .ms-dot { width: 8px; height: 8px; border-radius: 50%; background: rgba(255,255,255,0.3); }
    .ms-dot.active { background: #FFFFFF; }

    /* Stats bar */
    .ms-stats-bar {
        background: var(--ms-green);
        padding: 0;
        display: flex;
    }
    .ms-stat-item {
        flex: 1;
        padding: 28px 32px;
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.2);
    }
    .ms-stat-item:last-child { border-right: none; }
    .ms-stat-num {
        font-size: 28px;
        font-weight: 800;
        color: #FFFFFF;
        font-family: 'Inter', Arial, sans-serif;
        line-height: 1;
        margin-bottom: 4px;
    }
    .ms-stat-label {
        font-size: 12px;
        color: rgba(255,255,255,0.75);
        font-family: 'Inter', Arial, sans-serif;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Misi section */
    .ms-mission {
        padding: 80px 60px;
        display: flex;
        gap: 60px;
        align-items: center;
        background: #FFFFFF;
    }
    .ms-mission-img {
        flex: 1;
        border-radius: 16px;
        overflow: hidden;
        min-height: 380px;
        background: var(--ms-green);
        display: flex;
        align-items: center;
        justify-content: center;
        position: relative;
    }
    .ms-mission-txt { flex: 1.2; }
    .ms-mission-title {
        font-family: 'Inter', Arial, sans-serif !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #1A1A1A !important;
        line-height: 1.2 !important;
        margin: 0 0 16px 0 !important;
    }
    .ms-mission-desc {
        font-size: 15px;
        color: var(--ms-green);
        line-height: 1.7;
        margin-bottom: 32px;
        font-family: 'Inter', Arial, sans-serif;
    }
    .ms-mission-stats {
        display: flex;
        gap: 0;
        background: var(--ms-green);
        border-radius: 12px;
        overflow: hidden;
        margin-bottom: 24px;
    }
    .ms-mstat {
        flex: 1;
        padding: 16px 12px;
        text-align: center;
        border-right: 1px solid rgba(255,255,255,0.2);
    }
    .ms-mstat:last-child { border-right: none; }
    .ms-mstat-num { font-size: 20px; font-weight: 800; color: #FFF; font-family: 'Inter', Arial, sans-serif; }
    .ms-mstat-lbl { font-size: 11px; color: rgba(255,255,255,0.75); font-family: 'Inter', Arial, sans-serif; margin-top: 2px; }
    .ms-read-more {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        color: var(--ms-green);
        font-weight: 600;
        font-size: 15px;
        font-family: 'Inter', Arial, sans-serif;
        cursor: pointer;
        text-decoration: none;
        border-bottom: 2px solid var(--ms-green);
        padding-bottom: 2px;
    }

    /* Layanan Section */
    .ms-section-header {
        padding: 64px 60px 32px 60px;
        background: #FFFFFF;
    }
    .ms-section-title {
        font-family: 'Inter', Arial, sans-serif !important;
        font-size: 38px !important;
        font-weight: 800 !important;
        color: #1A1A1A !important;
        margin: 0 0 8px 0 !important;
        line-height: 1.2 !important;
    }
    .ms-section-sub {
        font-size: 15px;
        color: var(--ms-text-sub);
        font-family: 'Inter', Arial, sans-serif;
        margin: 0;
    }
    .ms-section-sub span { color: var(--ms-green); font-weight: 600; }

    /* Service Cards */
    .ms-service-card {
        border: 1.5px solid var(--ms-border);
        border-radius: 16px;
        padding: 28px 24px;
        background: #FFFFFF;
        transition: all 0.25s ease;
        height: 100%;
        min-height: 180px;
        cursor: pointer;
    }
    .ms-service-card:hover {
        border-color: var(--ms-green);
        box-shadow: 0 8px 32px rgba(26,155,75,0.12);
        transform: translateY(-2px);
    }
    .ms-service-icon {
        width: 48px; height: 48px;
        border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        font-size: 24px;
        margin-bottom: 16px;
    }
    .ms-service-name {
        font-family: 'Inter', Arial, sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #1A1A1A;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .ms-service-desc {
        font-family: 'Inter', Arial, sans-serif;
        font-size: 14px;
        color: #555;
        line-height: 1.6;
    }

    /* Waste Type Section */
    .ms-waste-section {
        background: var(--ms-green-bg);
        padding: 64px 60px;
    }
    .ms-waste-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-top: 40px;
    }
    .ms-waste-item {
        background: #FFFFFF;
        border: 1.5px solid var(--ms-border);
        border-radius: 16px;
        padding: 28px 16px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    .ms-waste-item:hover {
        border-color: var(--ms-green);
        box-shadow: 0 4px 20px rgba(26,155,75,0.12);
        transform: translateY(-2px);
    }
    .ms-waste-icon { font-size: 36px; margin-bottom: 12px; }
    .ms-waste-name {
        font-family: 'Inter', Arial, sans-serif;
        font-size: 14px;
        font-weight: 700;
        color: #1A1A1A;
    }

    /* Solutions */
    .ms-solutions {
        padding: 80px 60px;
        background: #FFFFFF;
    }
    .ms-sol-card {
        border-radius: 16px;
        overflow: hidden;
        cursor: pointer;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .ms-sol-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 16px 48px rgba(0,0,0,0.12);
    }
    .ms-sol-img {
        height: 240px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 64px;
        position: relative;
        overflow: hidden;
    }
    .ms-sol-body {
        padding: 24px;
        background: #FFFFFF;
        border: 1.5px solid var(--ms-border);
        border-top: none;
        border-radius: 0 0 16px 16px;
    }
    .ms-sol-title {
        font-family: 'Inter', Arial, sans-serif;
        font-size: 18px;
        font-weight: 800;
        color: #1A1A1A;
        margin-bottom: 8px;
    }
    .ms-sol-desc {
        font-size: 14px;
        color: #555;
        font-family: 'Inter', Arial, sans-serif;
        line-height: 1.6;
        margin-bottom: 20px;
    }
    .ms-sol-btn {
        display: inline-block;
        border: 1.5px solid var(--ms-green);
        color: var(--ms-green);
        padding: 10px 20px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        font-family: 'Inter', Arial, sans-serif;
        cursor: pointer;
        transition: all 0.2s;
    }
    .ms-sol-btn:hover { background: var(--ms-green); color: #fff; }

    /* CTA Green Section */
    .ms-cta-section {
        background: var(--ms-green);
        padding: 100px 60px;
        text-align: center;
        position: relative;
        overflow: hidden;
    }
    .ms-cta-section::before {
        content: '';
        position: absolute;
        top: -50%; left: -10%;
        width: 60%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.08) 0%, transparent 70%);
        pointer-events: none;
    }
    .ms-cta-title {
        font-family: 'Inter', Arial, sans-serif !important;
        font-size: 44px !important;
        font-weight: 800 !important;
        color: #FFFFFF !important;
        margin: 0 0 16px 0 !important;
        line-height: 1.2 !important;
        position: relative;
        z-index: 1;
    }
    .ms-cta-sub {
        font-size: 17px;
        color: rgba(255,255,255,0.85);
        margin-bottom: 40px;
        font-family: 'Inter', Arial, sans-serif;
        position: relative;
        z-index: 1;
    }
    .ms-cta-btns {
        display: flex;
        gap: 16px;
        justify-content: center;
        flex-wrap: wrap;
        position: relative;
        z-index: 1;
    }
    .ms-btn-white {
        background: #FFFFFF;
        color: var(--ms-green);
        padding: 14px 32px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 700;
        font-family: 'Inter', Arial, sans-serif;
        cursor: pointer;
        border: none;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .ms-btn-white:hover { box-shadow: 0 8px 24px rgba(0,0,0,0.2); transform: translateY(-1px); }
    .ms-btn-outline {
        background: transparent;
        color: #FFFFFF;
        padding: 14px 32px;
        border-radius: 10px;
        font-size: 16px;
        font-weight: 700;
        font-family: 'Inter', Arial, sans-serif;
        cursor: pointer;
        border: 2px solid rgba(255,255,255,0.6);
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }
    .ms-btn-outline:hover { border-color: #fff; background: rgba(255,255,255,0.1); }

    /* Footer */
    .ms-footer {
        background: #0F3D22;
        padding: 40px 60px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 16px;
    }
    .ms-footer-logo { font-size: 20px; font-weight: 800; color: #FFFFFF; font-family: 'Inter', Arial, sans-serif; }
    .ms-footer-sub { font-size: 13px; color: rgba(255,255,255,0.55); font-family: 'Inter', Arial, sans-serif; margin-top: 4px; }
    .ms-footer-right { font-size: 13px; color: rgba(255,255,255,0.55); font-family: 'Inter', Arial, sans-serif; }

    /* Hide Streamlit CTA buttons in landing page */
    .ms-hidden-btn { display: none !important; }

    /* Leaderboard preview */
    .ms-lb-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 14px 24px;
        border-bottom: 1px solid #EEEEEE;
        font-family: 'Inter', Arial, sans-serif;
        font-size: 14px;
        transition: background 0.2s;
    }
    .ms-lb-row:hover { background: #F9FFF9; }
    .ms-lb-row.top { background: var(--ms-green); border: none; border-radius: 10px 10px 0 0; }
    .ms-lb-name { font-weight: 600; color: #1A1A1A; }
    .ms-lb-name.top { color: #fff; }
    .ms-lb-nim { font-size: 12px; color: #888; }
    .ms-lb-nim.top { color: rgba(255,255,255,0.7); }
    .ms-lb-pts { font-weight: 700; color: var(--ms-green); }
    .ms-lb-pts.top { color: #fff; }
    .ms-lb-rank { width: 28px; font-weight: 700; color: #aaa; font-size: 13px; }
    .ms-lb-rank.top { color: rgba(255,255,255,0.8); }

    /* ==========================================
       RESPONSIVE DESIGN (MOBILE & TABLET)
       ========================================== */
    @media (max-width: 768px) {
        /* Navbar */
        .ms-nav {
            padding: 0 20px !important;
        }
        .ms-nav-logo {
            font-size: 18px !important;
        }
        .ms-nav-links {
            display: none !important; /* Hide menu links on mobile */
        }
        div.st-key-nav_login_btn {
            right: 20px !important;
        }

        /* Hero */
        .ms-hero {
            min-height: 60vh !important;
        }
        .ms-hero-content {
            padding: 0 24px !important;
        }
        .ms-hero h1 {
            font-size: 32px !important;
        }
        .ms-hero-sub {
            font-size: 15px !important;
        }

        /* Stats Bar */
        .ms-stats-bar {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
        }
        .ms-stat-item {
            padding: 18px 16px !important;
            border-right: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.15) !important;
        }
        .ms-stat-item:nth-child(even) {
            border-right: none !important;
        }
        .ms-stat-item:nth-child(odd) {
            border-right: 1px solid rgba(255,255,255,0.15) !important;
        }
        .ms-stat-item:nth-child(3), .ms-stat-item:nth-child(4) {
            border-bottom: none !important;
        }
        .ms-stat-num {
            font-size: 22px !important;
        }

        /* Misi Kami Section */
        .ms-mission-img {
            min-height: 240px !important;
            margin: 20px !important;
            height: 250px !important;
        }
        .ms-mission-txt {
            padding: 20px !important;
        }
        .ms-mission-title {
            font-size: 24px !important;
        }
        .ms-mission-desc {
            font-size: 14px !important;
            margin-bottom: 20px !important;
        }
        .ms-mission-stats {
            display: grid !important;
            grid-template-columns: repeat(2, 1fr) !important;
        }
        .ms-mstat {
            border-right: none !important;
            border-bottom: 1px solid rgba(255,255,255,0.15) !important;
        }
        .ms-mstat:nth-child(even) {
            border-right: none !important;
        }
        .ms-mstat:nth-child(odd) {
            border-right: 1px solid rgba(255,255,255,0.15) !important;
        }
        .ms-mstat:nth-child(3), .ms-mstat:nth-child(4) {
            border-bottom: none !important;
        }

        /* Layanan Section */
        .ms-section-header {
            padding: 40px 20px 20px 20px !important;
        }
        .ms-section-title {
            font-size: 24px !important;
        }
        .ms-section-sub {
            font-size: 14px !important;
        }
        .ms-service-card {
            margin-bottom: 16px !important;
        }

        /* Waste Grid */
        .ms-waste-section {
            padding: 40px 20px !important;
        }
        .ms-waste-grid {
            grid-template-columns: repeat(2, 1fr) !important;
            gap: 12px !important;
            margin-top: 24px !important;
        }

        /* Solutions */
        .ms-solutions {
            padding: 40px 20px !important;
        }
        .ms-sol-card {
            margin-bottom: 24px !important;
        }

        /* CTA Section */
        .ms-cta-section {
            padding: 60px 20px !important;
        }
        .ms-cta-title {
            font-size: 24px !important;
        }
        .ms-cta-sub {
            font-size: 14px !important;
        }

        /* Footer */
        .ms-footer {
            padding: 40px 20px !important;
            flex-direction: column !important;
            text-align: center !important;
            gap: 24px !important;
        }
        .ms-footer-right {
            text-align: center !important;
        }
    }
</style>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 1. NAVIGATION BAR & HERO SECTION - Combined to eliminate layout gaps
        # ──────────────────────────────────────────
        hero_bg_css = f"background-image: url('{hero_b64}'); background-size: cover; background-position: center;" if hero_b64 else "background: var(--ms-green);"
        st.markdown(f"""
<style>
/* Enable native smooth scroll behavior */
html {{
    scroll-behavior: smooth !important;
}}

/* Style and position the native Streamlit button absolutely over the navbar */
div.st-key-nav_login_btn {{
    position: fixed !important;
    top: 12px !important;
    right: 60px !important;
    z-index: 10000 !important;
    width: auto !important;
}}

div.st-key-nav_login_btn button, div.st-key-nav_login_btn button[data-testid*="stBaseButton"] {{
    background-color: #1A9B4B !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 22px !important;
    font-size: 14px !important;
    font-weight: 700 !important;
    font-family: 'Inter', Arial, sans-serif !important;
    cursor: pointer !important;
    transition: background-color 0.2s !important;
    height: 40px !important;
    box-shadow: none !important;
    transform: none !important;
    line-height: 1 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
}}

div.st-key-nav_login_btn button:hover, div.st-key-nav_login_btn button[data-testid*="stBaseButton"]:hover {{
    background-color: #157A3C !important;
    color: #FFFFFF !important;
}}

.ms-nav-logo {{
    display: inline-block !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #1A9B4B !important;
    letter-spacing: -0.5px !important;
    text-decoration: none !important;
}}

.ms-nav-link {{
    display: inline-block !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    color: #333333 !important;
    padding: 6px 18px !important;
    border-radius: 6px !important;
    cursor: pointer !important;
    text-decoration: none !important;
    transition: all 0.2s !important;
}}
.ms-nav-link:hover {{
    color: #1A9B4B !important;
    background-color: #E8F5EE !important;
}}
</style>
<div class="ms-nav">
    <a href="#" class="ms-nav-logo" style="text-decoration: none !important;">Mayasih</a>
    <div class="ms-nav-links">
        <a href="#tentang-kami" class="ms-nav-link">Tentang Kami</a>
        <a href="#layanan" class="ms-nav-link">Layanan &#9662;</a>
        <a href="#" class="ms-nav-link" onclick="alert('Fitur Solusi Daur Ulang & Kampus Hijau Mayasih sedang disiapkan!')">Solusi &#9662;</a>
        <a href="#leaderboard" class="ms-nav-link">Leaderboard</a>
        <a href="#" class="ms-nav-link" onclick="alert('Blog & Info Kegiatan Lingkungan Mahasiswa Mayasih akan segera hadir!')">Blog</a>
        <a href="#kontak-kami" class="ms-nav-link">Kontak Kami</a>
    </div>
    <div style="width: 100px; height: 40px;"></div>
</div>

<div class="ms-hero" style="{hero_bg_css}">
    <div class="ms-hero-overlay"></div>
    <div class="ms-hero-dots">
        <div class="ms-dot"></div>
        <div class="ms-dot active"></div>
        <div class="ms-dot"></div>
    </div>
    <div class="ms-hero-content">
        <div class="ms-hero-tag">🎓 Khusus Universitas Mayasari Bakti</div>
        <h1>Recycling for<br>Campus</h1>
        <p class="ms-hero-sub">Platform daur ulang & pelaporan sampah untuk seluruh civitas akademika kampus.</p>
        <p class="ms-hero-hashtag">#ubahjadikebaikan</p>
    </div>
</div>
""", unsafe_allow_html=True)

        if st.button("Masuk", key="nav_login_btn"):
            st.session_state.show_login = True
            st.session_state.login_role = 'user'
            st.rerun()

        # ──────────────────────────────────────────
        # 3. STATISTICS BAR - MallSampah Style
        # ──────────────────────────────────────────
        # Get live stats from DB
        total_users = db_session.query(User).filter_by(role='user').count()
        from models import Laporan, Reward, PenukaranReward
        total_laporan = db_session.query(Laporan).count() if hasattr(Laporan, '__table__') else 0
        total_penukaran = db_session.query(PenukaranReward).count() if hasattr(PenukaranReward, '__table__') else 0
        total_reward = db_session.query(Reward).count() if hasattr(Reward, '__table__') else 0

        st.markdown(f"""
<div class="ms-stats-bar">
    <div class="ms-stat-item">
        <div class="ms-stat-num">{max(total_laporan * 100, 500)}+</div>
        <div class="ms-stat-label">Poin Terdistribusi</div>
    </div>
    <div class="ms-stat-item">
        <div class="ms-stat-num">{max(total_laporan, 10)}+</div>
        <div class="ms-stat-label">Laporan Sampah</div>
    </div>
    <div class="ms-stat-item">
        <div class="ms-stat-num">{max(total_users, 5)}+</div>
        <div class="ms-stat-label">Mahasiswa Aktif</div>
    </div>
    <div class="ms-stat-item">
        <div class="ms-stat-num">{max(total_reward, 10)}+</div>
        <div class="ms-stat-label">Hadiah Tersedia</div>
    </div>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 4. MISI KAMI - Image left + Text right (MallSampah style)
        # ──────────────────────────────────────────
        st.markdown("<div id='tentang-kami' style='height: 1px; margin-top: -1px;'></div>", unsafe_allow_html=True)
        img_col, txt_col = st.columns([1, 1.3], gap="medium")
        with img_col:
            if sorting_b64:
                st.markdown(f"""
<div style="border-radius: 16px; overflow: hidden; height: 400px; margin: 32px 0 32px 32px; position: relative; background: var(--ms-green);">
    <img src="{sorting_b64}" style="width:100%; height:100%; object-fit:cover;" />
    <div style="position:absolute; bottom:0; left:0; right:0; background: linear-gradient(to top, rgba(20,100,55,0.9) 0%, transparent 60%); padding: 24px;">
        <div style="font-family:'Inter',sans-serif; color:#fff; font-size:16px; font-weight:700; line-height:1.3;">We are The<br>Recycling Network</div>
        <div style="font-size:13px; color:rgba(255,255,255,0.8); margin-top:4px; font-family:'Inter',sans-serif;">#ubahjadikebaikan</div>
    </div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(f"""
<div style="border-radius:16px; height:400px; margin:32px 0 32px 32px; background: var(--ms-green); display:flex; flex-direction:column; align-items:center; justify-content:center;">
    <div style="font-size:60px;">♻️</div>
    <div style="font-family:'Inter',sans-serif; color:#fff; font-size:18px; font-weight:700; margin-top:16px;">We are The<br>Recycling Network</div>
    <div style="font-size:13px; color:rgba(255,255,255,0.8); margin-top:8px;">#ubahjadikebaikan</div>
</div>
""", unsafe_allow_html=True)

        with txt_col:
            st.markdown("""
<div style="padding: 48px 48px 48px 24px;">
    <h2 class="ms-mission-title">Misi Kami Mewujudkan<br>Kampus Bersih & Hijau</h2>
    <p class="ms-mission-desc">
        Mayasih dirancang untuk menangkap masalah sampah langsung dari sumbernya di lingkungan kampus,
        dengan memanfaatkan partisipasi mahasiswa dan sistem verifikasi admin sebagai kunci rantai
        kebersihan di Universitas Mayasari Bakti.
    </p>

    <div class="ms-mission-stats">
        <div class="ms-mstat">
            <div class="ms-mstat-num">+100</div>
            <div class="ms-mstat-lbl">Poin / Laporan</div>
        </div>
        <div class="ms-mstat">
            <div class="ms-mstat-num">3</div>
            <div class="ms-mstat-lbl">Tier Reward</div>
        </div>
        <div class="ms-mstat">
            <div class="ms-mstat-num">60s</div>
            <div class="ms-mstat-lbl">Kuis Interaktif</div>
        </div>
        <div class="ms-mstat">
            <div class="ms-mstat-num">4</div>
            <div class="ms-mstat-lbl">Fitur Utama</div>
        </div>
    </div>

    <a class="ms-read-more">Semua Tentang Kami di sini →</a>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 5. LAYANAN SECTION - MallSampah Service Cards
        # ──────────────────────────────────────────
        st.markdown("""
<div id="layanan" class="ms-section-header" style="border-top: 1px solid #EEEEEE;">
    <h2 class="ms-section-title">Layanan</h2>
    <p class="ms-section-sub">Revolusi kebersihan kampus dari <span>Mayasih</span> untuk civitas akademika.</p>
</div>
""", unsafe_allow_html=True)

        svc1, svc2, svc3, svc4 = st.columns(4, gap="small")
        services = [
            ("📸", "#E8F5EE", "Lapor Sampah",
             "Foto tumpukan sampah, pilih kategori & lokasi kampus. Kolektor & petugas kebersihan akan merespons laporanmu.",
             "+100 Poin instan"),
            ("🧠", "#EEF2FF", "Kuis Interaktif",
             "Uji pengetahuanmu soal lingkungan. Jawab benar 100% dalam 60 detik dan raup poin bonus.",
             "+20 Poin bonus"),
            ("📚", "#FFF8EE", "Edukasi Lingkungan",
             "Baca artikel lokal kampus & web eksternal. Setiap artikel baru yang dibaca memberikan poin tambahan.",
             "+10 Poin / artikel"),
            ("🎁", "#FFF0F0", "Tukar Reward",
             "Voucher kantin, tumbler bambu, tote bag, pulsa - tersedia dalam 3 tier mulai dari 150 poin.",
             "3 Tier Hadiah"),
        ]
        for col, (icon, bg, name, desc, badge) in zip([svc1, svc2, svc3, svc4], services):
            with col:
                st.markdown(f"""
<div class="ms-service-card">
    <div class="ms-service-icon" style="background:{bg}; font-size:28px; width:52px; height:52px; border-radius:14px; display:flex; align-items:center; justify-content:center;">{icon}</div>
    <div class="ms-service-name">{name}</div>
    <p class="ms-service-desc">{desc}</p>
    <div style="margin-top:12px; display:inline-block; background:#E8F5EE; color:#1A9B4B; font-size:12px; font-weight:700; padding:4px 12px; border-radius:100px; font-family:'Inter',sans-serif;">{badge}</div>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 6. JENIS SAMPAH - MallSampah Waste Grid
        # ──────────────────────────────────────────
        st.markdown("""
<div class="ms-waste-section">
    <h2 class="ms-section-title">Jenis Sampah yang Dapat Dilaporkan</h2>
    <p class="ms-section-sub">Lihat semua jenis sampah yang dapat kamu laporkan di kampus.</p>
    <div class="ms-waste-grid">
        <div class="ms-waste-item">
            <div class="ms-waste-icon">📄</div>
            <div class="ms-waste-name">Kertas</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">🥤</div>
            <div class="ms-waste-name">Plastik</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">🔩</div>
            <div class="ms-waste-name">Logam</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">🌿</div>
            <div class="ms-waste-name">Organik</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">💻</div>
            <div class="ms-waste-name">Elektronik</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">🍶</div>
            <div class="ms-waste-name">Botol Kaca</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">🧴</div>
            <div class="ms-waste-name">Kemasan</div>
        </div>
        <div class="ms-waste-item">
            <div class="ms-waste-icon">❓</div>
            <div class="ms-waste-name">Lainnya</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 7. SOLUSI KAMI - MallSampah Solutions Cards
        # ──────────────────────────────────────────
        st.markdown("""
<div style="background: #FFFFFF; padding: 64px 60px 32px 60px; border-top: 1px solid #EEEEEE;">
    <h2 class="ms-section-title">Solusi Kami</h2>
    <p class="ms-section-sub">Sebuah ekosistem untuk menjaga kebersihan kampus bersama.</p>
</div>
""", unsafe_allow_html=True)

        sol1, sol2, sol3 = st.columns(3, gap="medium")
        solutions = [
            ("🎓", "#1A9B4B", "For Mahasiswa",
             "Laporkan sampah di kampus, dapatkan poin, tukar hadiah nyata. Jadilah agen perubahan lingkungan.",
             waste_b64),
            ("👩‍🏫", "#2563EB", "For Dosen & Staff",
             "Pantau kebersihan area kampus, verifikasi laporan mahasiswa, dan kelola program edukasi lingkungan.",
             dosen_b64),
            ("🏫", "#DC2626", "For Kampus",
             "Dashboard analitik lengkap untuk manajemen kebersihan kampus. Data real-time & laporan komprehensif.",
             kampus_b64),
        ]
        for col, (icon, color, title, desc, img_b64) in zip([sol1, sol2, sol3], solutions):
            with col:
                img_content = f'<img src="{img_b64}" style="width:100%;height:100%;object-fit:cover;" />' if img_b64 else f'<div style="font-size:64px;">{icon}</div>'
                st.markdown(f"""
<div class="ms-sol-card">
    <div class="ms-sol-img" style="background: linear-gradient(135deg, {color}22 0%, {color}44 100%); border-radius:16px 16px 0 0;">
        {img_content}
        <div style="position:absolute; bottom:16px; left:16px; background:{color}; color:#fff; border-radius:8px; padding:6px 14px; font-size:13px; font-weight:700; font-family:'Inter',sans-serif;">{title}</div>
    </div>
    <div class="ms-sol-body">
        <div class="ms-sol-title">{title}</div>
        <p class="ms-sol-desc">{desc}</p>
        <div class="ms-sol-btn">Cari Tahu →</div>
    </div>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 8. MATRIKS POIN + LEADERBOARD LIVE
        # ──────────────────────────────────────────
        st.markdown("""<div style="background:#FFFFFF; border-top: 1px solid #EEEEEE;"></div>""", unsafe_allow_html=True)
        mtx_col, lb_col = st.columns([1, 1], gap="medium")

        with mtx_col:
            st.markdown("""
<div style="padding: 64px 48px;">
    <h2 class="ms-section-title" style="font-size:32px!important;">Matriks Poin</h2>
    <p class="ms-section-sub" style="margin-bottom:32px;">Setiap aksi punya nilai yang jelas dan transparan.</p>

    <div style="border-top:2px solid #1A9B4B; margin-top:16px;">
        <div style="display:flex; justify-content:space-between; padding:14px 0; border-bottom:1px solid #EEE; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">📸 Kirim Laporan Sampah</span>
            <span style="font-weight:700; color:#1A9B4B;">+100 poin</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:14px 0; border-bottom:1px solid #EEE; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">✅ Laporan Diverifikasi Selesai</span>
            <span style="font-weight:700; color:#1A9B4B;">+150 poin</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:14px 0; border-bottom:1px solid #EEE; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">🧠 Kuis Benar 100% &lt; 60 detik</span>
            <span style="font-weight:700; color:#1A9B4B;">+20 poin</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:14px 0; border-bottom:1px solid #EEE; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">📚 Baca Materi Lokal</span>
            <span style="font-weight:700; color:#1A9B4B;">+10 poin</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:14px 0; border-bottom:1px solid #EEE; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">🌐 Baca Artikel Web Eksternal</span>
            <span style="font-weight:700; color:#1A9B4B;">+10 poin</span>
        </div>
        <div style="display:flex; justify-content:space-between; padding:14px 0; font-family:'Inter',sans-serif; font-size:14px;">
            <span style="color:#333;">🎁 Penukaran Reward</span>
            <span style="font-weight:700; color:#DC2626;">-X poin</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        with lb_col:
            st.markdown("""
<div id="leaderboard" style="padding: 64px 48px 32px 48px;">
    <h2 class="ms-section-title" style="font-size:32px!important;">Top Mahasiswa</h2>
    <p class="ms-section-sub" style="margin-bottom:24px;">Diperbarui real-time setiap aksi tercatat.</p>
</div>
""", unsafe_allow_html=True)
            users_list = db_session.query(User).filter_by(role='user').order_by(User.total_poin.desc()).limit(5).all()
            if users_list:
                for idx, u in enumerate(users_list):
                    is_top = idx == 0
                    cls = "top" if is_top else ""
                    medal = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"][idx]
                    st.markdown(f"""
<div class="ms-lb-row {cls}">
    <div style="display:flex; align-items:center; gap:16px;">
        <span style="font-size:20px;">{medal}</span>
        <div>
            <div class="ms-lb-name {cls}">{u.nama}</div>
            <div class="ms-lb-nim {cls}">NIM {u.nim}</div>
        </div>
    </div>
    <div class="ms-lb-pts {cls}">{u.total_poin} poin</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown("""
<div style="padding: 32px 48px; color:#888; font-family:'Inter',sans-serif; font-size:14px;">
    Belum ada mahasiswa terdaftar. Jadilah yang pertama!
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 9. REWARD PREVIEW SECTION
        # ──────────────────────────────────────────
        st.markdown("<div style='height:1px; background:#EEEEEE;'></div>", unsafe_allow_html=True)
        rew_img_col, rew_txt_col = st.columns([1, 1.2], gap="medium")
        with rew_img_col:
            if rewards_b64:
                st.markdown(f"""
<div style="border-radius:16px; overflow:hidden; height:460px; margin:40px 0 40px 40px;">
    <img src="{rewards_b64}" style="width:100%; height:100%; object-fit:cover;" />
</div>
""", unsafe_allow_html=True)
        with rew_txt_col:
            st.markdown("""
<div style="padding: 60px 48px;">
    <h2 class="ms-section-title">Poin yang Terasa Nyata</h2>
    <p style="font-size:15px; color:#1A9B4B; line-height:1.7; margin-bottom:32px; font-family:'Inter',sans-serif; font-weight:500;">
        Tiga tingkatan reward - dari voucher harian hingga merchandise edisi terbatas.<br>
        Tukar kodenya, scan, ambil hadiahmu langsung di kampus.
    </p>

    <div style="border-top:1px solid #EEE; padding:16px 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:#1A1A1A;">Tier 1 - Starter</div>
            <div style="font-size:13px; color:#888; font-family:'Inter',sans-serif; margin-top:2px;">Voucher Kantin 10K - Stiker - Pin Mayasih</div>
        </div>
        <div style="font-family:'Inter',sans-serif; font-size:13px; font-weight:700; color:#1A9B4B; white-space:nowrap;">150 – 400 poin</div>
    </div>

    <div style="border-top:1px solid #EEE; padding:16px 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:#1A1A1A;">Tier 2 - Enthusiast</div>
            <div style="font-size:13px; color:#888; font-family:'Inter',sans-serif; margin-top:2px;">Tumbler Bambu - Tote Bag - Pulsa 25K</div>
        </div>
        <div style="font-family:'Inter',sans-serif; font-size:13px; font-weight:700; color:#1A9B4B; white-space:nowrap;">600 – 1.200 poin</div>
    </div>

    <div style="border-top:1px solid #EEE; border-bottom:1px solid #EEE; padding:16px 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="font-family:'Inter',sans-serif; font-size:15px; font-weight:700; color:#1A1A1A;">Tier 3 - Champion</div>
            <div style="font-size:13px; color:#888; font-family:'Inter',sans-serif; margin-top:2px;">Voucher Buku 100K - Power Bank - Limited</div>
        </div>
        <div style="font-family:'Inter',sans-serif; font-size:13px; font-weight:700; color:#1A9B4B; white-space:nowrap;">1.600 – 2.500 poin</div>
    </div>
</div>
""", unsafe_allow_html=True)

        # ──────────────────────────────────────────
        # 10. FINAL CTA - MallSampah Green CTA (button embedded in HTML)
        # ──────────────────────────────────────────
        st.markdown("""
<style>
.ms-cta-masuk {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #FFFFFF;
    color: #1A9B4B;
    padding: 14px 40px;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 800;
    font-family: 'Inter', Arial, sans-serif;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    margin-top: 8px;
}
.ms-cta-masuk:hover { transform: translateY(-2px); box-shadow: 0 8px 28px rgba(0,0,0,0.2); }
</style>
<div class="ms-cta-section">
    <h2 class="ms-cta-title">Satu NIM. Satu Langkah.<br>Kampus Lebih Hijau.</h2>
    <p class="ms-cta-sub">Masuk hanya dengan Nomor Induk Mahasiswa. Mulai laporkan,<br>belajar, dan kumpulkan poin hari ini juga.</p>
    <div style="height: 50px;"></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<style>
div.st-key-cta_login_btn {
    position: relative !important;
    margin-top: -150px !important;
    margin-bottom: 100px !important;
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    z-index: 10 !important;
    width: 100% !important;
}
div.st-key-cta_login_btn div.stButton {
    display: inline-block !important;
    width: auto !important;
}
div.st-key-cta_login_btn button, div.st-key-cta_login_btn button[data-testid*="stBaseButton"] {
    background-color: #FFFFFF !important;
    color: #1A9B4B !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 14px 40px !important;
    font-size: 16px !important;
    font-weight: 800 !important;
    font-family: 'Inter', Arial, sans-serif !important;
    cursor: pointer !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15) !important;
    transition: all 0.2s !important;
    height: auto !important;
    line-height: 1 !important;
    width: auto !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
}
div.st-key-cta_login_btn button:hover, div.st-key-cta_login_btn button[data-testid*="stBaseButton"]:hover {
    background-color: #FFFFFF !important;
    color: #1A9B4B !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.2) !important;
}
</style>
""", unsafe_allow_html=True)
        if st.button("🎓 Masuk dengan NIM", key="cta_login_btn"):
            st.session_state.show_login = True
            st.session_state.login_role = 'user'
            st.rerun()

        # ──────────────────────────────────────────
        # 11. FOOTER - Dark Green
        # ──────────────────────────────────────────
        st.markdown("""
<div id="kontak-kami" class="ms-footer">
    <div>
        <div class="ms-footer-logo">Mayasih</div>
        <div class="ms-footer-sub">Mayasari Bersih - Universitas Mayasari Bakti</div>
        <div class="ms-footer-sub" style="margin-top:4px;">#ubahjadikebaikan</div>
    </div>
    <div style="display:flex; gap:40px; flex-wrap:wrap;">
        <div>
            <div style="color:rgba(255,255,255,0.4); font-size:11px; font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Platform</div>
            <div class="ms-footer-sub">Lapor Sampah</div>
            <div class="ms-footer-sub" style="margin-top:4px;">Edukasi</div>
            <div class="ms-footer-sub" style="margin-top:4px;">Kuis Interaktif</div>
            <div class="ms-footer-sub" style="margin-top:4px;">Reward Center</div>
        </div>
        <div>
            <div style="color:rgba(255,255,255,0.4); font-size:11px; font-family:'Inter',sans-serif; text-transform:uppercase; letter-spacing:1px; margin-bottom:8px;">Tentang</div>
            <div class="ms-footer-sub">Misi Kami</div>
            <div class="ms-footer-sub" style="margin-top:4px;">Leaderboard</div>
            <div class="ms-footer-sub" style="margin-top:4px;">Kontak</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)



    else:
        # ── LOGIN PAGE - Green gradient background, white card ──
        st.markdown("""
<style>
/* Full-page green gradient background for login */
.stApp {
    background: linear-gradient(135deg, #0d5c2f 0%, #1A9B4B 40%, #22c55e 100%) !important;
}
/* Override Streamlit block container for login */
.block-container {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    min-height: 100vh !important;
    padding: 0 !important;
}
.login-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 48px 40px 40px 40px;
    box-shadow: 0 24px 64px rgba(0,0,0,0.25);
    text-align: center;
    max-width: 480px;
    width: 100%;
    margin: 0 auto;
}
.login-logo {
    font-family: 'Inter', Arial, sans-serif;
    font-size: 22px;
    font-weight: 800;
    color: #1A9B4B;
    letter-spacing: -0.5px;
    margin-bottom: 4px;
}
.login-title {
    font-family: 'Inter', Arial, sans-serif !important;
    font-size: 30px !important;
    font-weight: 800 !important;
    color: #1A1A1A !important;
    margin: 0 0 6px 0 !important;
    line-height: 1.2 !important;
}
.login-sub {
    font-size: 14px;
    color: #666;
    font-family: 'Inter', Arial, sans-serif;
    margin-bottom: 28px;
}
/* Style Streamlit tabs inside login */
div[data-testid="stTabBar"] {
    background: #F0FAF4 !important;
    border-radius: 10px !important;
    padding: 4px !important;
    border: none !important;
    margin-bottom: 20px !important;
}
div[data-testid="stTabBar"] button {
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 13px !important;
    color: #555 !important;
}
div[data-testid="stTabBar"] button[aria-selected="true"] {
    background: #1A9B4B !important;
    color: #FFFFFF !important;
    border-bottom: none !important;
}

@media (max-width: 480px) {
    .login-card {
        padding: 32px 20px 24px 20px !important;
        border-radius: 12px !important;
        width: 90% !important;
    }
    .login-title {
        font-size: 24px !important;
    }
}
</style>
""", unsafe_allow_html=True)

        left_sp, login_container, right_sp = st.columns([1, 1.4, 1])
        with login_container:
            st.markdown("""
<div class="login-card">
    <div class="login-logo">🌿 Mayasih</div>
    <h2 class="login-title">Masuk Portal</h2>
    <p class="login-sub">Universitas Mayasari Bakti - #ubahjadikebaikan</p>
</div>
""", unsafe_allow_html=True)
            
            # Registration Flow for new Mahasiswa NIM
            if st.session_state.register_mode:
                st.warning("⚠️ NIM BARU TERDETEKSI")
                st.write(f"NIM **{st.session_state.temp_nim}** belum terdaftar di basis data Mayasih.")
                st.write("Silakan masukkan nama lengkap Anda untuk melakukan registrasi mandiri:")
                
                reg_name = st.text_input("Nama Lengkap", placeholder="Contoh: Ahmad Fauzi")
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("SIMPAN & MASUK", type="primary", use_container_width=True):
                        if reg_name.strip():
                            # Create User
                            new_user = User(
                                nim=st.session_state.temp_nim,
                                nama=reg_name.strip(),
                                total_poin=0,
                                role='user'
                            )
                            db_session.add(new_user)
                            db_session.commit()
                            
                            # Set Login State
                            st.session_state.user_id = new_user.id
                            st.session_state.role = 'user'
                            st.session_state.register_mode = False
                            st.session_state.temp_nim = None
                            st.session_state.show_login = False
                            st.success(f"Registrasi Berhasil! Selamat datang, {new_user.nama}.")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Nama lengkap wajib diisi.")
                with c2:
                    if st.button("BATAL", use_container_width=True):
                        st.session_state.register_mode = False
                        st.session_state.temp_nim = None
                        st.rerun()
                            
            else:
                # Login Type Selection using tabs
                login_tabs = st.tabs(["MAHASISWA", "ADMINISTRATOR"])
                
                with login_tabs[0]:
                    nim_input = st.text_input("Nomor Induk Mahasiswa (NIM)", placeholder="Masukkan NIM Anda", key="nim_input_main")
                    c_lg_1, c_lg_2 = st.columns(2)
                    with c_lg_1:
                        if st.button("MASUK MAHASISWA", use_container_width=True, type="primary", key="mahasiswa_login_btn"):
                            if nim_input.strip():
                                user = db_session.query(User).filter(User.nim == nim_input.strip()).first()
                                if user:
                                    st.session_state.user_id = user.id
                                    st.session_state.role = user.role
                                    st.session_state.show_login = False
                                    st.success(f"Selamat datang kembali, {user.nama}!")
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.session_state.temp_nim = nim_input.strip()
                                    st.session_state.register_mode = True
                                    st.rerun()
                            else:
                                st.error("NIM wajib diisi.")
                    with c_lg_2:
                        if st.button("KEMBALI", use_container_width=True, key="mahasiswa_back_btn"):
                            st.session_state.show_login = False
                            st.rerun()
                            
                with login_tabs[1]:
                    email_input = st.text_input("Email Administrator", placeholder="admin@mayasih.id", key="email_input_main")
                    pass_input = st.text_input("Password", type="password", placeholder="••••••••", key="pass_input_main")
                    c_ad_1, c_ad_2 = st.columns(2)
                    with c_ad_1:
                        if st.button("MASUK ADMIN", use_container_width=True, type="primary", key="admin_login_btn"):
                            admin = db_session.query(User).filter(User.email == email_input.strip(), User.role == 'admin').first()
                            if admin and check_password_hash(admin.password, pass_input.strip()):
                                st.session_state.user_id = admin.id
                                st.session_state.role = 'admin'
                                st.session_state.show_login = False
                                st.success("Login Administrator Berhasil!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.error("Kredensial administrator tidak valid.")
                    with c_ad_2:
                        if st.button("KEMBALI", use_container_width=True, key="admin_back_btn"):
                            st.session_state.show_login = False
                            st.rerun()

# ----------------- MAIN APP STATE (LOGGED IN) -----------------
else:
    # Load logged in user
    current_user = db_session.query(User).get(st.session_state.user_id)
    
    # Auto logout if user not found in database anymore
    if not current_user:
        st.session_state.user_id = None
        st.session_state.role = None
        st.rerun()
        
    # --- GREEN BRAND SIDEBAR STYLE ---
    st.markdown("""
<style>
/* Sidebar green brand redesign */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d5c2f 0%, #1A9B4B 100%) !important;
    border-right: none !important;
    font-family: 'Inter', Arial, sans-serif !important;
}
[data-testid="stSidebar"] button,
[data-testid="stSidebar"] select,
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
    font-family: 'Inter', Arial, sans-serif !important;
}

/* Sidebar navigation buttons overrides - using specific selectors to beat the global blue button style */
div[data-testid="stSidebar"] .stButton > button {
    background-color: transparent !important;
    color: rgba(255, 255, 255, 0.8) !important;
    border: none !important;
    border-radius: 8px !important;
    text-align: left !important;
    justify-content: flex-start !important;
    transition: all 0.2s ease-in-out !important;
    padding: 10px 16px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    min-height: auto !important;
    width: 100% !important;
    box-shadow: none !important;
    transform: none !important;
}

div[data-testid="stSidebar"] .stButton > button:hover {
    background-color: rgba(255, 255, 255, 0.12) !important;
    color: #FFFFFF !important;
}

/* Active navigation button in sidebar */
div[data-testid="stSidebar"] .stButton > button[kind="primary"],
div[data-testid="stSidebar"] button[data-testid*="primary"] {
    background-color: rgba(255, 255, 255, 0.2) !important;
    color: #FFFFFF !important;
    border: 1.5px solid rgba(255, 255, 255, 0.45) !important;
    font-weight: 700 !important;
}

div[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
div[data-testid="stSidebar"] button[data-testid*="primary"]:hover {
    background-color: rgba(255, 255, 255, 0.3) !important;
}

/* Main content area reset to white */
.stApp {
    background-color: #F8FAF9 !important;
}
/* Main content cards redesign */
.brutalist-card, .tesla-card {
    background: #FFFFFF !important;
    border: 1.5px solid #EEEEEE !important;
    border-radius: 14px !important;
    padding: 24px !important;
    box-shadow: 0 2px 12px rgba(26,155,75,0.06) !important;
    transition: box-shadow 0.2s, transform 0.2s !important;
}
.brutalist-card:hover, .tesla-card:hover {
    box-shadow: 0 6px 24px rgba(26,155,75,0.13) !important;
    transform: translateY(-2px) !important;
    background: #FFFFFF !important;
}

/* Premium Gradient Metric Cards */
.card-metric {
    border-radius: 16px !important;
    padding: 24px !important;
    margin-bottom: 16px !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.03) !important;
    transition: transform 0.25s ease, box-shadow 0.25s ease !important;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 140px;
    border: 1px solid rgba(0, 0, 0, 0.04) !important;
}
.card-metric:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 24px rgba(26,155,75,0.1) !important;
}

.card-metric-1 {
    background: linear-gradient(135deg, #F0FDF4 0%, #DCFCE7 100%) !important;
    border-left: 5px solid #16A34A !important;
}

.card-metric-2 {
    background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%) !important;
    border-left: 5px solid #2563EB !important;
}

.card-metric-3 {
    background: linear-gradient(135deg, #FEFCE8 0%, #FEF9C3 100%) !important;
    border-left: 5px solid #CA8A04 !important;
}

.card-metric-4 {
    background: linear-gradient(135deg, #064E3B 0%, #047857 100%) !important;
    color: #FFFFFF !important;
    border-left: 5px solid #34D399 !important;
    box-shadow: 0 10px 20px rgba(4, 120, 87, 0.15) !important;
}
.card-metric-4:hover {
    box-shadow: 0 16px 30px rgba(4, 120, 87, 0.25) !important;
}

/* Progress Bar Premium Redesign */
div[data-testid="stProgress"] > div {
    background-color: #E8F5E9 !important;
    border-radius: 8px !important;
    height: 10px !important;
}
div[data-testid="stProgress"] > div > div {
    background: linear-gradient(90deg, #1A9B4B 0%, #2E7D32 100%) !important;
    border-radius: 8px !important;
}

/* Tab bar in main area */
div[data-testid="stTabBar"] {
    border-bottom: 2px solid #1A9B4B !important;
}
div[data-testid="stTabBar"] button {
    color: #393C41 !important;
    font-weight: 500 !important;
}
div[data-testid="stTabBar"] button[aria-selected="true"] {
    color: #1A9B4B !important;
    font-weight: 700 !important;
    border-bottom: 2px solid #1A9B4B !important;
}

/* Force visible dark text for all main content widgets and labels */
[data-testid="stWidgetLabel"], 
.stWidgetLabel, 
label:not([class*="card-metric"] *),
.stMarkdown p:not([class*="card-metric"] *),
.stMarkdown span:not([class*="card-metric"] *) {
    color: #171A20 !important;
}

/* Radio Buttons Text Contrast */
[data-testid="stRadio"] label,
[data-testid="stRadio"] span,
[data-testid="stRadio"] p,
[data-testid="stRadio"] div {
    color: #171A20 !important;
}

/* Select Box Text Contrast */
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] span,
[data-testid="stSelectbox"] div {
    color: #171A20 !important;
}

/* Text Inputs and Text Areas Labels */
[data-testid="stTextInput"] label,
[data-testid="stTextInput"] span,
[data-testid="stTextInput"] p,
[data-testid="stTextArea"] label,
[data-testid="stTextArea"] span,
[data-testid="stTextArea"] p {
    color: #171A20 !important;
}

/* Expander Header Text Contrast */
[data-testid="stExpander"] summary,
[data-testid="stExpander"] p,
[data-testid="stExpander"] span,
[data-testid="stExpander"] div {
    color: #171A20 !important;
}

/* File Uploader Text Contrast */
[data-testid="stFileUploader"] label,
[data-testid="stFileUploader"] span,
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] div {
    color: #171A20 !important;
}
</style>
""", unsafe_allow_html=True)

    # --- SIDEBAR NAV ---
    with st.sidebar:
        # Green brand header
        role_icon = "🛡️" if current_user.role == 'admin' else "🎓"
        st.markdown(f"""
<div style="padding: 28px 16px 20px 16px; border-bottom: 1px solid rgba(255,255,255,0.2); margin-bottom: 16px;">
    <div style="font-size: 22px; font-weight: 800; color: #FFFFFF; letter-spacing: -0.5px;">🌿 Mayasih</div>
    <div style="font-size: 12px; color: rgba(255,255,255,0.65); margin-top: 2px; font-weight: 500;">Universitas Mayasari Bakti</div>
</div>
""", unsafe_allow_html=True)

        # User profile badge - green card style
        poin_line = f"<div style='font-size: 15px; font-weight: 800; color: #FFFFFF; margin-top: 6px;'>✨ {current_user.total_poin} poin</div>" if current_user.role == 'user' else ""
        role_text = f"NIM {current_user.nim}" if current_user.role == 'user' else "Administrator"
        role_badge_color = "#FCD34D" if current_user.role == 'admin' else "rgba(255,255,255,0.25)"
        st.markdown(f"""
<div style="margin: 0 8px 16px 8px; padding: 14px 16px; background: rgba(255,255,255,0.15); border-radius: 12px; border: 1px solid rgba(255,255,255,0.25);">
    <div style="font-size: 15px; font-weight: 700; color: #FFFFFF;">{role_icon} {current_user.nama}</div>
    <div style="font-size: 12px; color: rgba(255,255,255,0.7); margin-top: 2px;">{role_text}</div>
    {poin_line}
</div>
""", unsafe_allow_html=True)

        # Nav label
        st.markdown("<div style='color: rgba(255,255,255,0.45); padding: 0 16px 8px 16px; font-size: 11px; font-weight: 600; letter-spacing: 1.5px; text-transform: uppercase;'>NAVIGASI</div>", unsafe_allow_html=True)

        if current_user.role == 'admin':
            menu_options = [
                "Dashboard Analitik",
                "Verifikasi Laporan",
                "Kelola Edukasi",
                "Kelola Quiz",
                "Kelola Reward",
                "Manajemen User"
            ]
        else:
            menu_options = [
                "Dashboard",
                "Edukasi Lingkungan",
                "Quiz Interaktif",
                "Lapor Sampah",
                "Reward Center",
                "Leaderboard",
                "Profil Saya"
            ]

        for opt in menu_options:
            if st.button(opt, use_container_width=True, type="primary" if st.session_state.page == opt else "secondary"):
                st.session_state.page = opt
                st.rerun()

        st.markdown("<div style='height:1px; background:rgba(255,255,255,0.15); margin: 12px 16px;'></div>", unsafe_allow_html=True)
        if st.button("⏻  Keluar Sistem", use_container_width=True, type="secondary"):
            st.session_state.user_id = None
            st.session_state.role = None
            st.session_state.page = "Dashboard"
            st.success("Anda telah keluar dari sistem.")
            time.sleep(1)
            st.rerun()

    # --- MAIN PAGE CONTENTS ---
    
    # ----------------- STUDENT MENU PAGES -----------------
    if current_user.role == 'user':
        
        # 1. STUDENT DASHBOARD
        if st.session_state.page == "Dashboard":
            st.markdown("""
<h1 style='font-family: Inter, Arial, sans-serif; font-weight: 500; color: #171A20; font-size: 40px; margin: 24px 0 4px 0;'>Dashboard</h1>
""", unsafe_allow_html=True)
            st.markdown("<p style='color: #5C5E62; font-size: 14px; margin: 0 0 24px 0;'>Ringkasan aktivitas dan kontribusi Anda di Universitas Mayasari Bakti.</p>", unsafe_allow_html=True)
            
            # Retrieve counts and ranks
            total_laporan = db_session.query(Laporan).filter_by(user_id=current_user.id).count()
            
            edukasi_selesai = db_session.query(RiwayatPoin).filter(
                RiwayatPoin.user_id == current_user.id,
                RiwayatPoin.aktivitas.like('Membaca materi:%')
            ).count()
            
            # Leaderboard rank calculation
            all_users = db_session.query(User).filter_by(role='user').order_by(User.total_poin.desc()).all()
            user_rank = 1
            for index, u in enumerate(all_users):
                if u.id == current_user.id:
                    user_rank = index + 1
                    break
                    
            # Tier progress reward
            next_reward = db_session.query(Reward).filter(Reward.poin_dibutuhkan > current_user.total_poin).order_by(Reward.poin_dibutuhkan.asc()).first()
            if not next_reward:
                next_reward = db_session.query(Reward).order_by(Reward.poin_dibutuhkan.desc()).first()
                
            # Stats metrics columns
            st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
<div class="card-metric card-metric-1">
    <div style="font-size: 12px; font-weight: 600; color: #15803D; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">📋 Laporan Saya</div>
    <div style="font-size: 40px; font-weight: 800; color: #166534; line-height: 1.2; font-family: 'Inter', sans-serif;">{total_laporan}</div>
    <div style="font-size: 13px; color: #166534; margin-top: 4px; font-family: 'Inter', sans-serif;">Laporan Terkirim</div>
</div>
""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
<div class="card-metric card-metric-2">
    <div style="font-size: 12px; font-weight: 600; color: #1D4ED8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">📚 Edukasi Selesai</div>
    <div style="font-size: 40px; font-weight: 800; color: #1E40AF; line-height: 1.2; font-family: 'Inter', sans-serif;">{edukasi_selesai}</div>
    <div style="font-size: 13px; color: #1E40AF; margin-top: 4px; font-family: 'Inter', sans-serif;">Materi Dibaca</div>
</div>
""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
<div class="card-metric card-metric-3">
    <div style="font-size: 12px; font-weight: 600; color: #A16207; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">🏆 Peringkat Kampus</div>
    <div style="font-size: 40px; font-weight: 800; color: #854D0E; line-height: 1.2; font-family: 'Inter', sans-serif;">#{user_rank}</div>
    <div style="font-size: 13px; color: #854D0E; margin-top: 4px; font-family: 'Inter', sans-serif;">Dari {len(all_users)} Mahasiswa</div>
</div>
""", unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
<div class="card-metric card-metric-4">
    <div style="font-size: 12px; font-weight: 600; color: #A7F3D0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">✨ Poin Saya</div>
    <div style="font-size: 40px; font-weight: 800; color: #FFFFFF; line-height: 1.2; font-family: 'Inter', sans-serif;">{current_user.total_poin}</div>
    <div style="font-size: 13px; color: #D1FAE5; margin-top: 4px; font-family: 'Inter', sans-serif;">Gunakan di Reward Center</div>
</div>
""", unsafe_allow_html=True)
                
            # Reward tier progress bar
            if next_reward:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-family: Inter, sans-serif; font-size: 14px; font-weight: 500; color: #171A20;'>Target reward berikutnya: <span style='color: #1A9B4B; font-weight: 600;'>{next_reward.nama_reward}</span></p>", unsafe_allow_html=True)
                req_poin = next_reward.poin_dibutuhkan
                cur_poin = current_user.total_poin
                progress_percent = min(1.0, float(cur_poin) / float(req_poin)) if req_poin > 0 else 1.0
                
                st.progress(progress_percent)
                st.markdown(f"<p style='font-family: Inter, sans-serif; font-size: 14px; color: #5C5E62;'>Kemajuan: {cur_poin} / {req_poin} poin ({int(progress_percent*100)}%)</p>", unsafe_allow_html=True)
                
            # Recent Activity & Leaderboard columns
            st.markdown("<hr>", unsafe_allow_html=True)
            left_col, right_col = st.columns([3, 2], gap="large")
            
            with left_col:
                st.markdown("<h3 style='font-family: Inter, sans-serif; font-size: 18px; font-weight: 600; color: #171A20; margin-bottom: 16px;'>Aktivitas Poin Terbaru</h3>", unsafe_allow_html=True)
                recent_activities = db_session.query(RiwayatPoin).filter_by(user_id=current_user.id).order_by(RiwayatPoin.tanggal.desc()).limit(5).all()
                if recent_activities:
                    for act in recent_activities:
                        pts_class = "color: #1A9B4B;" if act.jumlah_poin >= 0 else "color: #DC2626;"
                        st.markdown(f"""
                        <div style="padding: 14px 20px; background-color: #FFFFFF; border: 1px solid #EEEEEE; margin-bottom: 0.8rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                            <div>
                                <span style="font-weight: 600; color: #171A20; font-family: 'Inter', sans-serif; font-size: 14px;">{act.aktivitas}</span><br>
                                <span style="font-size: 11px; color: #8E8E8E; font-weight: 400; font-family: 'Inter', sans-serif;">{act.tanggal.strftime('%d %b %Y, %H:%M UTC')}</span>
                            </div>
                            <div style="font-weight: 700; font-family: 'Inter', sans-serif; font-size: 15px; {pts_class}">
                                {'+' if act.jumlah_poin >= 0 else ''}{act.jumlah_poin} POIN
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Belum ada riwayat aktivitas poin.")
                    
            with right_col:
                st.markdown("<h3 style='font-family: Inter, sans-serif; font-size: 18px; font-weight: 600; color: #171A20; margin-bottom: 16px;'>🏆 Top 5 Leaderboard</h3>", unsafe_allow_html=True)
                top_contributors = db_session.query(User).filter_by(role='user').order_by(User.total_poin.desc()).limit(5).all()
                
                for idx, u in enumerate(top_contributors):
                    is_current = "border: 2px solid #1A9B4B;" if u.id == current_user.id else "border: 1px solid #EEEEEE;"
                    bg_color = "background-color: rgba(26, 155, 75, 0.05);" if u.id == current_user.id else "background-color: #FFFFFF;"
                    medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f" {idx+1}. "
                    st.markdown(f"""
                    <div style="padding: 14px 20px; {bg_color} {is_current} margin-bottom: 0.6rem; border-radius: 12px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                        <div style="font-weight: 600; color: #171A20; font-family: 'Inter', sans-serif; font-size: 14px;">{medal} {u.nama}</div>
                        <div style="font-weight: 700; font-family: 'Inter', sans-serif; color: #1A9B4B; font-size: 15px;">{u.total_poin} POIN</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 2. STUDENT EDUKASI LINGKUNGAN
        elif st.session_state.page == "Edukasi Lingkungan":
            st.title("📚 EDUKASI LINGKUNGAN")
            st.markdown("<p style='color: #8a8a8a;'>Membaca artikel edukasi lingkungan untuk menambah wawasan dan poin.</p>", unsafe_allow_html=True)
            
            edu_tabs = st.tabs(["Materi Lokal Kampus", "Cari Edukasi dari Web (Google Search) 🔍"])
            
            with edu_tabs[0]:
                articles = db_session.query(Edukasi).order_by(Edukasi.tanggal.desc()).all()
                
                # Fetch what articles student read
                read_activities = db_session.query(RiwayatPoin).filter(
                    RiwayatPoin.user_id == current_user.id,
                    RiwayatPoin.aktivitas.like('Membaca materi:%')
                ).all()
                read_titles = [rp.aktivitas.replace('Membaca materi: ', '') for rp in read_activities]
                
                if articles:
                    for art in articles:
                        is_read = art.judul in read_titles
                        status_tag = "<span style='background-color: #E8F5EE; color: #1A9B4B; padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 12px; font-family: \"Inter\", sans-serif;'>SELESAI DIBACA</span>" if is_read else "<span style='background-color: #FFF3CD; color: #856404; padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 12px; font-family: \"Inter\", sans-serif;'>BELUM DIBACA</span>"
                        
                        st.markdown(f"""
                        <div class="brutalist-card">
                            <span style="font-size: 11px; color: #1A9B4B; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; font-family: 'Inter', sans-serif;">{art.kategori}</span>
                            <h3 style="margin: 6px 0 12px 0; color: #171A20; font-family: 'Inter', sans-serif; font-size: 20px; font-weight: 600;">{art.judul}</h3>
                            <p style="font-size: 14px; color: #393C41; line-height: 1.6; font-family: 'Inter', sans-serif;">{art.isi[:180]}...</p>
                            <div style="margin-top: 15px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #EEEEEE; padding-top: 12px;">
                                <span style="font-size: 12px; color: #8E8E8E; font-weight: 400; font-family: 'Inter', sans-serif;">Diterbitkan: {art.tanggal.strftime('%d %b %Y')}</span>
                                {status_tag}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        with st.expander(f"Baca Selengkapnya: {art.judul}"):
                            st.markdown(f"<div style='font-family: \"Inter\", sans-serif; font-size: 15px; line-height: 1.7; color: #393C41; padding: 10px 0;'>{art.isi}</div>", unsafe_allow_html=True)
                            if not is_read:
                                if st.button(f"Selesai Membaca & Klaim 10 Poin", key=f"read_btn_{art.id}", type="primary"):
                                    add_user_points(db_session, current_user, 10, f"Membaca materi: {art.judul}")
                                    st.success("Selamat! Anda mendapatkan 10 poin.")
                                    time.sleep(1)
                                    st.rerun()
                else:
                    st.info("Materi edukasi lokal belum tersedia.")
                    
            with edu_tabs[1]:
                st.write("Temukan artikel edukasi dari internet. Baca dan dapatkan **10 poin** untuk setiap artikel baru.")
                query_search = st.text_input("Topik pencarian sampah / lingkungan", placeholder="contoh: daur ulang plastik, kompos daun kering")
                
                if query_search:
                    st.write(f"Menampilkan hasil pencarian untuk: **{query_search}**")
                    with st.spinner("Mengambil artikel dari internet..."):
                        search_results = search_web_articles(query_search)
                        
                    if search_results:
                        # Fetch reading history for web articles
                        web_read_activities = db_session.query(RiwayatPoin).filter(
                            RiwayatPoin.user_id == current_user.id,
                            RiwayatPoin.aktivitas.like('Membaca materi web:%')
                        ).all()
                        read_web_titles = [rp.aktivitas.replace('Membaca materi web: ', '') for rp in web_read_activities]
                        
                        for idx, res in enumerate(search_results):
                            title = res['title']
                            link = res['link']
                            snippet = res['snippet']
                            
                            is_read = title in read_web_titles
                            status_text = "💚 Dibaca (+10 Poin)" if is_read else "📖 Belum Dibaca"
                            
                            st.markdown(f"""
                            <div style="padding: 18px 22px; background-color: #FFFFFF; border: 1px solid #EEEEEE; margin-bottom: 0.8rem; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.01);">
                                <a href="{link}" target="_blank" style="font-size: 16px; color: #3E6AE1; font-family: 'Inter', sans-serif; font-weight: 600; text-decoration: none;">{title}</a>
                                <p style="font-size: 12px; color: #8E8E8E; margin: 6px 0; font-weight: 400; font-family: 'Inter', sans-serif;">URL: {link}</p>
                                <p style="font-size: 14px; color: #393C41; line-height: 1.6; margin: 0; font-family: 'Inter', sans-serif;">{snippet}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            c1, c2 = st.columns([1, 4])
                            with c1:
                                if is_read:
                                    st.info("Sudah diklaim")
                                else:
                                    if st.button(f"Klaim Poin Membaca", key=f"claim_web_{idx}", type="primary"):
                                        add_user_points(db_session, current_user, 10, f"Membaca materi web: {title}")
                                        st.success(f"Poin berhasil diklaim untuk artikel: {title}")
                                        time.sleep(1)
                                        st.rerun()
                            st.write("")
                    else:
                        st.warning("Tidak ditemukan artikel tentang topik tersebut. Silakan coba kata kunci lain.")

        # 3. STUDENT QUIZ INTERAKTIF
        elif st.session_state.page == "Quiz Interaktif":
            st.title("🧩 QUIZ INTERAKTIF")
            st.markdown("<p style='color: #8a8a8a;'>Uji pemahaman Anda dari materi edukasi. Jawab dalam batas waktu untuk meraih **20 poin**!</p>", unsafe_allow_html=True)
            
            # Reset active quiz if clicked elsewhere
            if st.session_state.active_quiz_id is not None:
                st.info("⏳ Kuis sedang berjalan. Harap selesaikan kuis di bawah ini:")
                
                # Fetch questions
                art_id = st.session_state.active_quiz_id
                article = db_session.query(Edukasi).get(art_id)
                quizzes = db_session.query(Quiz).filter_by(edukasi_id=art_id).all()
                
                if not quizzes:
                    st.error("Kuis untuk materi ini belum dikonfigurasi.")
                    if st.button("Kembali ke Daftar Kuis"):
                        st.session_state.active_quiz_id = None
                        st.session_state.quiz_start_time = None
                        st.rerun()
                else:
                    # Timer Logic
                    time_limit = 60 # seconds
                    elapsed = time.time() - st.session_state.quiz_start_time
                    remaining = time_limit - elapsed
                    
                    st.markdown(f"### Kuis: {article.judul}")
                    
                    if remaining <= 0:
                        st.error("🚨 WAKTU HABIS! Anda tidak menyelesaikan kuis dalam waktu 60 detik.")
                        if st.button("Coba Lagi / Kembali"):
                            st.session_state.active_quiz_id = None
                            st.session_state.quiz_start_time = None
                            st.rerun()
                    else:
                        st.warning(f"🕒 Waktu Tersisa: **{int(remaining)} detik** (Halaman refresh saat Anda melakukan interaksi)")
                        
                        # Render Form
                        with st.form("quiz_form"):
                            answers = {}
                            for q in quizzes:
                                st.markdown(f"""
                                <div class="quiz-box" style="background-color: #F4F4F4; border-left: 4px solid #1A9B4B; padding: 14px 20px; border-radius: 8px;">
                                    <div style="font-weight: 600; color: #171A20; font-size: 15px; font-family: 'Inter', sans-serif; margin-bottom: 4px;">Soal: {q.pertanyaan}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                options = {
                                    "A": f"A. {q.pilihan_a}",
                                    "B": f"B. {q.pilihan_b}",
                                    "C": f"C. {q.pilihan_c}",
                                    "D": f"D. {q.pilihan_d}"
                                }
                                
                                ans = st.radio(
                                    "Pilih jawaban Anda:", 
                                    options=list(options.keys()), 
                                    format_func=lambda x: options[x],
                                    key=f"q_ans_{q.id}"
                                )
                                answers[q.id] = ans
                                
                            submit_quiz = st.form_submit_button("SUBMIT JAWABAN KUIS")
                            
                            if submit_quiz:
                                # Re-check timer at submit instant
                                final_elapsed = time.time() - st.session_state.quiz_start_time
                                if final_elapsed > time_limit:
                                    st.error("🚨 Maaf, Anda terlambat mengirimkan jawaban. Waktu sudah melebihi 60 detik.")
                                else:
                                    correct_count = 0
                                    total_questions = len(quizzes)
                                    for q in quizzes:
                                        if answers[q.id] == q.jawaban_benar:
                                            correct_count += 1
                                            
                                    if correct_count == total_questions:
                                        # Reward 20 points
                                        add_user_points(db_session, current_user, 20, f"Menyelesaikan quiz: {article.judul}")
                                        st.balloons()
                                        st.success(f"🏆 LUAR BIASA! Semua jawaban benar ({correct_count}/{total_questions}) dalam waktu {int(final_elapsed)} detik. Anda mendapatkan 20 poin!")
                                    else:
                                        st.error(f"❌ Jawaban benar: {correct_count} dari {total_questions} soal. Anda harus menjawab benar semua untuk mendapatkan poin. Silakan coba lagi!")
                                    
                                    # Clear state
                                    st.session_state.active_quiz_id = None
                                    st.session_state.quiz_start_time = None
                                    
                                    # Button to return
                                    st.form_submit_button("Kembali ke Daftar Kuis")
            else:
                # Show list of quizzes
                articles_with_quizzes = db_session.query(Edukasi).join(Quiz).all()
                
                # Fetch completed quizzes
                completed_activities = db_session.query(RiwayatPoin).filter(
                    RiwayatPoin.user_id == current_user.id,
                    RiwayatPoin.aktivitas.like('Menyelesaikan quiz:%')
                ).all()
                completed_titles = [rp.aktivitas.replace('Menyelesaikan quiz: ', '') for rp in completed_activities]
                
                if articles_with_quizzes:
                    for art in articles_with_quizzes:
                        is_completed = art.judul in completed_titles
                        status_tag = "<span style='background-color: #E8F5EE; color: #1A9B4B; padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 12px; font-family: \"Inter\", sans-serif;'>SELESAI (+20 Poin)</span>" if is_completed else "<span style='background-color: #FFF3CD; color: #856404; padding: 6px 14px; border-radius: 8px; font-weight: 600; font-size: 12px; font-family: \"Inter\", sans-serif;'>BELUM SELESAI</span>"
                        
                        st.markdown(f"""
                        <div class="brutalist-card">
                            <span style="font-size: 11px; color: #1A9B4B; text-transform: uppercase; font-weight: 700; letter-spacing: 0.8px; font-family: 'Inter', sans-serif;">{art.kategori}</span>
                            <h3 style="margin: 6px 0 12px 0; color: #171A20; font-family: 'Inter', sans-serif; font-size: 18px; font-weight: 600;">Kuis: {art.judul}</h3>
                            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #EEEEEE; padding-top: 12px;">
                                <span style="font-size: 12px; color: #8E8E8E; font-weight: 400; font-family: 'Inter', sans-serif;">Batas Waktu: 60 detik</span>
                                {status_tag}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if is_completed:
                            st.info("Kuis ini telah berhasil diselesaikan sebelumnya.")
                        else:
                            if st.button(f"Mulai Kerjakan Kuis", key=f"start_quiz_{art.id}", type="primary"):
                                st.session_state.active_quiz_id = art.id
                                st.session_state.quiz_start_time = time.time()
                                st.rerun()
                else:
                    st.info("Kuis interaktif belum tersedia saat ini.")

        # 4. STUDENT LAPOR SAMPAH
        elif st.session_state.page == "Lapor Sampah":
            st.title("📸 LAPOR SAMPAH")
            st.markdown("<p style='color: #8a8a8a;'>Laporkan sampah berserakan di lingkungan kampus. Dapatkan **100 poin** instan!</p>", unsafe_allow_html=True)
            
            st.write("Pilih salah satu metode untuk mengambil foto sampah:")
            
            # Image Input Mode selection
            input_mode = st.radio("Metode Foto", ["Gunakan Kamera Perangkat 📸", "Unggah File Gambar 📁"])
            
            captured_file = None
            if input_mode == "Gunakan Kamera Perangkat 📸":
                captured_file = st.camera_input("Ambil Foto Sampah Secara Langsung")
            else:
                captured_file = st.file_uploader("Pilih file foto sampah", type=["png", "jpg", "jpeg"])
                
            lokasi = st.text_input("Lokasi Sampah", placeholder="contoh: Depan Tangga Lt.2 Fasilkom")
            kategori = st.selectbox("Kategori Sampah", ["Plastik", "Organik", "Kertas", "Logam", "Lainnya"])
            deskripsi = st.text_area("Deskripsi Singkat", placeholder="Sebutkan detail atau kendala sampah di lokasi tersebut")
            
            if st.button("KIRIM LAPORAN SAMPAH", type="primary"):
                if not captured_file or not lokasi.strip() or not deskripsi.strip():
                    st.error("Semua field laporan wajib diisi, termasuk foto sampah.")
                else:
                    # Save image file to static/uploads
                    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
                    
                    filename = f"{current_user.nim}_{int(time.time())}_{captured_file.name if hasattr(captured_file, 'name') and captured_file.name else 'cam.jpg'}"
                    filepath = os.path.join('static', 'uploads', filename)
                    
                    # Write file
                    with open(filepath, "wb") as f:
                        f.write(captured_file.read())
                        
                    # Create database Laporan record
                    laporan = Laporan(
                        user_id=current_user.id,
                        foto=filename,
                        lokasi=lokasi.strip(),
                        kategori_sampah=kategori,
                        deskripsi=deskripsi.strip(),
                        status='Menunggu Verifikasi',
                        tanggal=datetime.utcnow()
                    )
                    db_session.add(laporan)
                    db_session.commit()
                    
                    # Reward user 100 points
                    add_user_points(db_session, current_user, 100, f"Mengirim laporan: {lokasi.strip()}")
                    
                    st.success("Laporan sampah berhasil dikirim! Anda memperoleh 100 poin.")
                    time.sleep(1)
                    st.session_state.page = "Dashboard"
                    st.rerun()

        # 5. STUDENT REWARD CENTER
        elif st.session_state.page == "Reward Center":
            st.title("🎁 REWARD CENTER")
            st.markdown("<p style='color: #8a8a8a;'>Tukarkan akumulasi poin Anda dengan berbagai penawaran voucher menarik.</p>", unsafe_allow_html=True)
            
            # Claim history retrieval
            redemptions = db_session.query(PenukaranReward).filter_by(user_id=current_user.id).all()
            redeemed_ids = [r.reward_id for r in redemptions]
            
            # Fetch rewards grouped by Tiers
            for tier in [1, 2, 3]:
                st.subheader(f"🏷️ Rewards Tier {tier}")
                rewards = db_session.query(Reward).filter_by(tier=tier).all()
                
                if rewards:
                    cols = st.columns(min(len(rewards), 3))
                    for idx, rew in enumerate(rewards):
                        col_idx = idx % len(cols)
                        with cols[col_idx]:
                            is_claimed = rew.id in redeemed_ids
                            claim_status = "Claimed" if is_claimed else "Tukarkan"
                            
                            st.markdown(f"""
                            <div class="brutalist-card">
                                <span style="font-size: 11px; color: #1A9B4B; font-weight: 700; letter-spacing: 0.8px; font-family: 'Inter', sans-serif;">TIER {rew.tier}</span>
                                <h4 style="margin: 6px 0 12px 0; color: #171A20; font-family: 'Inter', sans-serif; font-size: 15px; font-weight: 600; min-height: 40px; line-height: 1.4;">{rew.nama_reward}</h4>
                                <div style="font-size: 18px; font-family: 'Inter', sans-serif; font-weight: 700; color: #1A9B4B; margin-bottom: 12px;">{rew.poin_dibutuhkan} <span style="font-size: 11px; font-weight: 500; color: #5C5E62;">POIN</span></div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if is_claimed:
                                st.info("Voucher ini sudah diklaim")
                            else:
                                if current_user.total_poin < rew.poin_dibutuhkan:
                                    st.button(f"Poin Kurang", key=f"rew_{rew.id}", disabled=True, use_container_width=True)
                                else:
                                    if st.button(f"Tukarkan Reward", key=f"rew_{rew.id}", type="primary", use_container_width=True):
                                        # Deduct user points
                                        current_user.total_poin -= rew.poin_dibutuhkan
                                        
                                        # Save penukaran record
                                        penukaran = PenukaranReward(
                                            user_id=current_user.id,
                                            reward_id=rew.id,
                                            tanggal_penukaran=datetime.utcnow()
                                        )
                                        
                                        # Log points deduction
                                        activity_name = f"Menukarkan reward: {rew.nama_reward}"
                                        rp = RiwayatPoin(
                                            user_id=current_user.id,
                                            aktivitas=activity_name,
                                            jumlah_poin=-rew.poin_dibutuhkan,
                                            tanggal=datetime.utcnow()
                                        )
                                        ak = Aktivitas(
                                            user_id=current_user.id,
                                            aktivitas=activity_name,
                                            poin=-rew.poin_dibutuhkan,
                                            created_at=datetime.utcnow()
                                        )
                                        
                                        db_session.add(penukaran)
                                        db_session.add(rp)
                                        db_session.add(ak)
                                        db_session.commit()
                                        
                                        st.success(f"Berhasil mengklaim: {rew.nama_reward}!")
                                        time.sleep(1)
                                        st.rerun()
                else:
                    st.info(f"Voucher Tier {tier} belum tersedia.")

        # 6. STUDENT LEADERBOARD
        elif st.session_state.page == "Leaderboard":
            st.title("🏆 LEADERBOARD KONTRIBUTOR")
            st.markdown("<p style='color: #8a8a8a;'>Daftar mahasiswa teraktif dalam pengumpulan poin kebersihan kampus.</p>", unsafe_allow_html=True)
            
            # Simple leaderboard display
            users = db_session.query(User).filter_by(role='user').order_by(User.total_poin.desc()).all()
            
            if users:
                leaderboard_data = []
                for idx, u in enumerate(users):
                    medal = "🥇" if idx == 0 else "🥈" if idx == 1 else "🥉" if idx == 2 else f"{idx+1}"
                    leaderboard_data.append({
                        "Peringkat": medal,
                        "Nama": u.nama,
                        "NIM": u.nim,
                        "Poin Kebersihan": f"{u.total_poin} POIN"
                    })
                st.table(leaderboard_data)
            else:
                st.info("Peringkat belum tersedia.")

        # 7. STUDENT PROFIL SAYA
        elif st.session_state.page == "Profil Saya":
            st.title("👤 PROFIL SAYA")
            st.markdown("<p style='color: #8a8a8a;'>Detail profil mahasiswa dan histori perolehan poin Anda.</p>", unsafe_allow_html=True)
            
            # Layout
            p1, p2 = st.columns([1, 2])
            with p1:
                st.markdown(f"""
                <div class="brutalist-card" style="text-align: center; font-family: 'Inter', sans-serif;">
                    <div style="font-size: 4rem; margin-bottom: 12px;">🎓</div>
                    <h3 style="font-family: 'Inter', sans-serif; font-weight: 600; color: #171A20; font-size: 20px; margin: 0 0 4px 0;">{current_user.nama}</h3>
                    <div style="color: #8E8E8E; font-size: 13px; font-family: 'Inter', sans-serif;">NIM: {current_user.nim}</div>
                    <div style="font-size: 22px; font-weight: 700; color: #1A9B4B; margin-top: 16px; font-family: 'Inter', sans-serif;">{current_user.total_poin} POIN</div>
                </div>
                """, unsafe_allow_html=True)
                
            with p2:
                prof_tabs = st.tabs(["Histori Poin", "Klaim Voucher Saya"])
                
                with prof_tabs[0]:
                    hist = db_session.query(RiwayatPoin).filter_by(user_id=current_user.id).order_by(RiwayatPoin.tanggal.desc()).all()
                    if hist:
                        for h in hist:
                            pt_sign = "+" if h.jumlah_poin >= 0 else ""
                            pt_color = "color: #1A9B4B;" if h.jumlah_poin >= 0 else "color: #DC2626;"
                            st.markdown(f"""
                            <div style="padding: 12px 0; border-bottom: 1px solid #EEEEEE; display: flex; justify-content: space-between; align-items: center; font-family: 'Inter', sans-serif;">
                                <div>
                                    <div style="font-weight: 600; color: #171A20; font-size: 14px;">{h.aktivitas}</div>
                                    <div style="font-size: 12px; color: #8E8E8E; margin-top: 2px;">{h.tanggal.strftime('%d %b %Y, %H:%M UTC')}</div>
                                </div>
                                <div style="font-weight: 700; font-size: 14px; {pt_color}">{pt_sign}{h.jumlah_poin} POIN</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Belum ada histori poin.")
                        
                with prof_tabs[1]:
                    claims = db_session.query(PenukaranReward).filter_by(user_id=current_user.id).order_by(PenukaranReward.tanggal_penukaran.desc()).all()
                    if claims:
                        for cl in claims:
                            reward_details = db_session.query(Reward).get(cl.reward_id)
                            st.markdown(f"""
                            <div style="padding: 16px; border: 1px dashed #1A9B4B; margin-bottom: 12px; background-color: #F0FAF4; border-radius: 8px; font-family: 'Inter', sans-serif;">
                                <div style="font-weight: 600; color: #171A20; font-size: 15px;">{reward_details.nama_reward}</div>
                                <div style="font-size: 12px; color: #5C5E62; margin-top: 4px;">Diklaim pada: {cl.tanggal_penukaran.strftime('%d %b %Y, %H:%M UTC')}</div>
                                <div style="font-size: 13px; color: #1A9B4B; font-weight: 700; margin-top: 10px; padding: 6px 12px; background: #FFFFFF; border: 1px solid #E8F5EE; border-radius: 4px; display: inline-block; letter-spacing: 0.5px;">KODE VOUCHER: MS-{reward_details.id}{cl.id}-{int(cl.tanggal_penukaran.timestamp()) % 10000}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("Anda belum memiliki voucher yang ditukarkan.")

    # ----------------- ADMIN MENU PAGES -----------------
    elif current_user.role == 'admin':
        
        # 1. ADMIN DASHBOARD ANALITIK
        if st.session_state.page == "Dashboard Analitik":
            st.title("📊 DASHBOARD ANALITIK ADMINISTRATOR")
            st.markdown("<p style='color: #8a8a8a;'>Overview performa kebersihan kampus Universitas Mayasari Bakti.</p>", unsafe_allow_html=True)
            
            # Fetch analytics stats
            total_students = db_session.query(User).filter_by(role='user').count()
            total_laporan = db_session.query(Laporan).count()
            laporan_diproses = db_session.query(Laporan).filter_by(status='Diproses').count()
            laporan_selesai = db_session.query(Laporan).filter_by(status='Selesai').count()
            reward_ditukar = db_session.query(PenukaranReward).count()
            
            # Impact estimates
            weight_handled = laporan_selesai * 2.5 # 2.5 kg estimated per solved report
            percentage_clean = round((laporan_selesai / total_laporan * 100), 1) if total_laporan > 0 else 100.0
            
            # Render stats metrics
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"""
                <div class="card-metric card-metric-1">
                    <div style="font-size: 12px; font-weight: 600; color: #15803D; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">Total Mahasiswa</div>
                    <div style="font-size: 38px; font-weight: 800; color: #166534; line-height: 1.2; font-family: 'Inter', sans-serif; margin: 4px 0;">{total_students}</div>
                    <div style="font-size: 13px; color: #166534; font-weight: 600; font-family: 'Inter', sans-serif;">Terdaftar Aktif</div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="card-metric card-metric-2">
                    <div style="font-size: 12px; font-weight: 600; color: #1D4ED8; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">Total Laporan Sampah</div>
                    <div style="font-size: 38px; font-weight: 800; color: #1E40AF; line-height: 1.2; font-family: 'Inter', sans-serif; margin: 4px 0;">{total_laporan}</div>
                    <div style="font-size: 13px; color: #1E40AF; font-weight: 600; font-family: 'Inter', sans-serif;">{laporan_diproses} Diproses / {laporan_selesai} Selesai</div>
                </div>
                """, unsafe_allow_html=True)
            with c3:
                st.markdown(f"""
                <div class="card-metric card-metric-3">
                    <div style="font-size: 12px; font-weight: 600; color: #A16207; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">Estimasi Beban Teratasi</div>
                    <div style="font-size: 38px; font-weight: 800; color: #854D0E; line-height: 1.2; font-family: 'Inter', sans-serif; margin: 4px 0;">{weight_handled} kg</div>
                    <div style="font-size: 13px; color: #854D0E; font-weight: 600; font-family: 'Inter', sans-serif;">Dari Laporan Selesai</div>
                </div>
                """, unsafe_allow_html=True)
            with c4:
                st.markdown(f"""
                <div class="card-metric card-metric-4">
                    <div style="font-size: 12px; font-weight: 600; color: #A7F3D0; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 8px; font-family: 'Inter', sans-serif;">Reward Diklaim</div>
                    <div style="font-size: 38px; font-weight: 800; color: #FFFFFF; line-height: 1.2; font-family: 'Inter', sans-serif; margin: 4px 0;">{reward_ditukar}</div>
                    <div style="font-size: 13px; color: #D1FAE5; font-family: 'Inter', sans-serif;">Telah Ditukar Mahasiswa</div>
                </div>
                """, unsafe_allow_html=True)
                
            # Chart Section
            st.write("---")
            left_col, right_col = st.columns([3, 2])
            
            with left_col:
                st.subheader("📊 Kategori Laporan Sampah")
                # Group reports by category and count
                cats = ['Plastik', 'Organik', 'Kertas', 'Logam', 'Lainnya']
                cat_data = {}
                for cat in cats:
                    count = db_session.query(Laporan).filter_by(kategori_sampah=cat).count()
                    cat_data[cat] = count
                    
                st.bar_chart(cat_data)
                
            with right_col:
                st.subheader("🏆 Mahasiswa Teraktif")
                top_active = db_session.query(User).filter_by(role='user').order_by(User.total_poin.desc()).limit(5).all()
                for idx, u in enumerate(top_active):
                    st.markdown(f"""
                    <div style="padding: 12px 16px; background-color: #FFFFFF; border: 1px solid #EEEEEE; margin-bottom: 0.5rem; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; font-family: 'Inter', sans-serif;">
                        <div style="font-weight: 600; color: #171A20; font-size: 14px;">{idx+1}. {u.nama} ({u.nim})</div>
                        <div style="font-weight: 700; color: #1A9B4B; font-size: 14px;">{u.total_poin} POIN</div>
                    </div>
                    """, unsafe_allow_html=True)

        # 2. ADMIN VERIFIKASI LAPORAN
        elif st.session_state.page == "Verifikasi Laporan":
            st.title("📋 VERIFIKASI LAPORAN MAHASISWA")
            st.markdown("<p style='color: #8a8a8a;'>Verifikasi pengaduan sampah yang dilaporkan mahasiswa dan setujui penambahan poin.</p>", unsafe_allow_html=True)
            
            reports = db_session.query(Laporan).order_by(Laporan.tanggal.desc()).all()
            
            if reports:
                for rep in reports:
                    reporter = db_session.query(User).get(rep.user_id)
                    reporter_name = reporter.nama if reporter else "Unknown"
                    
                    bg_color = "#E8F5EE" if rep.status == 'Selesai' else "#FFF8E1" if rep.status == 'Diproses' else "#FFEBEE"
                    border_color = "#1A9B4B" if rep.status == 'Selesai' else "#FFB300" if rep.status == 'Diproses' else "#E53935"
                    status_text_color = "#1A9B4B" if rep.status == 'Selesai' else "#FFB300" if rep.status == 'Diproses' else "#E53935"
                    
                    st.markdown(f"""
                    <div style="padding: 20px; background-color: {bg_color}; border: 1px solid {border_color}; border-radius: 12px; margin-bottom: 1rem; font-family: 'Inter', sans-serif;">
                        <h4 style="margin: 0; color: #171A20; font-family: 'Inter', sans-serif; font-size: 16px; font-weight: 600;">Lokasi: {rep.lokasi}</h4>
                        <div style="font-size: 12px; color: #5C5E62; margin: 6px 0; font-family: 'Inter', sans-serif;">Dilaporkan oleh: <b>{reporter_name}</b> ({reporter.nim if reporter else ''}) | Kategori: <b>{rep.kategori_sampah}</b></div>
                        <p style="font-size: 14px; color: #393C41; margin-top: 10px; line-height: 1.5; font-family: 'Inter', sans-serif;">Deskripsi: {rep.deskripsi}</p>
                        <div style="font-size: 13px; font-weight: 700; color: {status_text_color}; margin-top: 12px; font-family: 'Inter', sans-serif;">Status: {rep.status.upper()}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Display report image
                    img_path = os.path.join('static', 'uploads', rep.foto)
                    if os.path.exists(img_path):
                        st.image(img_path, width=300, caption=f"Foto Sampah - {rep.lokasi}")
                    else:
                        st.info("File gambar laporan tidak ditemukan.")
                        
                    # Verification control buttons
                    if rep.status != 'Selesai':
                        c1, c2 = st.columns(2)
                        with c1:
                            if rep.status == 'Menunggu Verifikasi':
                                if st.button(f"Proses Laporan #{rep.id}", key=f"proc_btn_{rep.id}", type="secondary"):
                                    rep.status = 'Diproses'
                                    db_session.commit()
                                    st.success(f"Status laporan #{rep.id} diubah menjadi Diproses.")
                                    time.sleep(0.5)
                                    st.rerun()
                        with c2:
                            if st.button(f"Selesaikan & Beri 150 Poin #{rep.id}", key=f"done_btn_{rep.id}", type="primary"):
                                old_status = rep.status
                                rep.status = 'Selesai'
                                
                                # Reward reporter 150 points for verifikasi
                                if old_status != 'Selesai' and reporter:
                                    activity_name = f"Laporan diverifikasi: {rep.lokasi}"
                                    # Ensure no duplicate reward logs for this report verification
                                    already_rewarded = db_session.query(RiwayatPoin).filter_by(user_id=reporter.id, aktivitas=activity_name).first() is not None
                                    if not already_rewarded:
                                        add_user_points(db_session, reporter, 150, activity_name)
                                        
                                db_session.commit()
                                st.success(f"Status laporan #{rep.id} dinyatakan Selesai. Reporter mendapatkan 150 poin tambahan!")
                                time.sleep(0.5)
                                st.rerun()
                    st.write("---")
            else:
                st.info("Belum ada laporan sampah masuk.")

        # 3. ADMIN KELOLA EDUKASI
        elif st.session_state.page == "Kelola Edukasi":
            st.title("📚 KELOLA EDUKASI KAMPUS")
            st.markdown("<p style='color: #8a8a8a;'>Tambahkan materi edukasi kebersihan kampus bagi mahasiswa.</p>", unsafe_allow_html=True)
            
            with st.form("add_edu_form"):
                judul = st.text_input("Judul Materi Edukasi", placeholder="contoh: Cara Membuat Kompos Cair")
                kategori = st.selectbox("Kategori", ["Pemilahan Sampah", "Sampah Plastik", "Daur Ulang", "Kampus Hijau"])
                isi = st.text_area("Isi Lengkap Artikel")
                
                submit_edu = st.form_submit_button("PUBLIKASIKAN MATERI")
                if submit_edu:
                    if not judul.strip() or not isi.strip():
                        st.error("Judul dan Isi artikel wajib diisi.")
                    else:
                        edukasi = Edukasi(
                            judul=judul.strip(),
                            kategori=kategori,
                            isi=isi.strip(),
                            tanggal=datetime.utcnow()
                        )
                        db_session.add(edukasi)
                        db_session.commit()
                        st.success(f"Materi '{judul.strip()}' berhasil ditambahkan!")
                        time.sleep(1)
                        st.rerun()
                        
            st.write("---")
            st.subheader("Daftar Artikel Terbit")
            articles = db_session.query(Edukasi).order_by(Edukasi.tanggal.desc()).all()
            if articles:
                for a in articles:
                    st.markdown(f"**[{a.kategori}] {a.judul}** - {a.tanggal.strftime('%d %b %Y')}")
                    if st.button("Hapus Artikel", key=f"del_edu_{a.id}"):
                        db_session.delete(a)
                        db_session.commit()
                        st.success("Materi berhasil dihapus.")
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.info("Belum ada materi edukasi ditambahkan.")

        # 4. ADMIN KELOLA QUIZ
        elif st.session_state.page == "Kelola Quiz":
            st.title("🧩 KELOLA QUIZ INTERAKTIF")
            st.markdown("<p style='color: #8a8a8a;'>Tambahkan pertanyaan kuis baru untuk menguji pemahaman materi mahasiswa.</p>", unsafe_allow_html=True)
            
            articles = db_session.query(Edukasi).all()
            
            if not articles:
                st.warning("Tambahkan materi edukasi terlebih dahulu sebelum mengonfigurasi quiz.")
            else:
                with st.form("add_quiz_form"):
                    edu_selection = st.selectbox("Pilih Artikel Terkait", options=articles, format_func=lambda x: f"[{x.kategori}] {x.judul}")
                    pertanyaan = st.text_input("Pertanyaan Kuis")
                    p_a = st.text_input("Pilihan A")
                    p_b = st.text_input("Pilihan B")
                    p_c = st.text_input("Pilihan C")
                    p_d = st.text_input("Pilihan D")
                    jawaban = st.selectbox("Jawaban Benar", ["A", "B", "C", "D"])
                    
                    submit_quiz = st.form_submit_button("SIMPAN PERTANYAAN KUIS")
                    if submit_quiz:
                        if not pertanyaan.strip() or not p_a.strip() or not p_b.strip() or not p_c.strip() or not p_d.strip():
                            st.error("Pertanyaan dan seluruh opsi jawaban A/B/C/D wajib diisi.")
                        else:
                            quiz = Quiz(
                                edukasi_id=edu_selection.id,
                                pertanyaan=pertanyaan.strip(),
                                pilihan_a=p_a.strip(),
                                pilihan_b=p_b.strip(),
                                pilihan_c=p_c.strip(),
                                pilihan_d=p_d.strip(),
                                jawaban_benar=jawaban
                            )
                            db_session.add(quiz)
                            db_session.commit()
                            st.success("Pertanyaan kuis berhasil ditambahkan!")
                            time.sleep(1)
                            st.rerun()
                            
                st.write("---")
                st.subheader("Daftar Soal Quiz Terpasang")
                quizzes = db_session.query(Quiz).all()
                if quizzes:
                    for q in quizzes:
                        art = db_session.query(Edukasi).get(q.edukasi_id)
                        art_title = art.judul if art else "Materi Dihapus"
                        st.markdown(f"**Materi: {art_title}**")
                        st.write(f"Soal: {q.pertanyaan}")
                        st.write(f"Jawaban Benar: {q.jawaban_benar} (A: {q.pilihan_a} | B: {q.pilihan_b} | C: {q.pilihan_c} | D: {q.pilihan_d})")
                        if st.button("Hapus Soal", key=f"del_q_{q.id}"):
                            db_session.delete(q)
                            db_session.commit()
                            st.success("Soal kuis berhasil dihapus.")
                            time.sleep(0.5)
                            st.rerun()
                        st.write("")
                else:
                    st.info("Belum ada soal quiz terpasang.")

        # 5. ADMIN KELOLA REWARD
        elif st.session_state.page == "Kelola Reward":
            st.title("🎁 KELOLA REWARD CENTER")
            st.markdown("<p style='color: #8a8a8a;'>Tambahkan voucher/barang baru yang bisa ditukarkan mahasiswa dengan poin mereka.</p>", unsafe_allow_html=True)
            
            with st.form("add_reward_form"):
                nama_reward = st.text_input("Nama Reward / Item Voucher", placeholder="contoh: Pulsa 10k")
                tier = st.selectbox("Tier Reward (1, 2, atau 3)", [1, 2, 3])
                poin = st.number_input("Poin yang Dibutuhkan", min_value=50, step=50, value=200)
                
                submit_reward = st.form_submit_button("PUBLIKASIKAN REWARD")
                if submit_reward:
                    if not nama_reward.strip():
                        st.error("Nama reward wajib diisi.")
                    else:
                        reward = Reward(
                            nama_reward=nama_reward.strip(),
                            tier=tier,
                            poin_dibutuhkan=poin
                        )
                        db_session.add(reward)
                        db_session.commit()
                        st.success(f"Reward '{nama_reward.strip()}' berhasil dipublikasikan!")
                        time.sleep(1)
                        st.rerun()
                        
            st.write("---")
            st.subheader("Daftar Reward Aktif")
            rewards = db_session.query(Reward).order_by(Reward.tier.asc(), Reward.poin_dibutuhkan.asc()).all()
            if rewards:
                for r in rewards:
                    st.markdown(f"**[Tier {r.tier}] {r.nama_reward}** - {r.poin_dibutuhkan} Poin")
                    if st.button("Hapus Reward", key=f"del_rew_{r.id}"):
                        db_session.delete(r)
                        db_session.commit()
                        st.success("Reward berhasil dihapus.")
                        time.sleep(0.5)
                        st.rerun()
            else:
                st.info("Belum ada item reward terdaftar.")

        # 6. ADMIN MANAJEMEN USER
        elif st.session_state.page == "Manajemen User":
            st.title("👥 MANAJEMEN USER MAHASISWA")
            st.markdown("<p style='color: #8a8a8a;'>Berikut adalah daftar mahasiswa yang terdaftar dalam program Mayasih.</p>", unsafe_allow_html=True)
            
            users = db_session.query(User).filter_by(role='user').order_by(User.nim.asc()).all()
            
            if users:
                user_list = []
                for idx, u in enumerate(users):
                    user_list.append({
                        "No": idx + 1,
                        "NIM": u.nim,
                        "Nama Lengkap": u.nama,
                        "Akumulasi Poin": f"{u.total_poin} POIN"
                    })
                st.table(user_list)
            else:
                st.info("Belum ada mahasiswa terdaftar.")

# Close database session
db_session.close()
