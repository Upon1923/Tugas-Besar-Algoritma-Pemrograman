import os

filepath = r"c:\Users\muhda\Downloads\Tubes Algoritma\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Define the combined navbar/hero block target and replacement
target_nav_hero = """        # ──────────────────────────────────────────
        # 1. NAVIGATION BAR & HERO SECTION — Combined to eliminate layout gaps
        # ──────────────────────────────────────────
        hero_bg_css = f"background-image: url('data:image/png;base64,{hero_b64}'); background-size: cover; background-position: center;" if hero_b64 else "background: var(--ms-green);"
        st.markdown(f\"\"\"
<style>
/* Make the injected Streamlit masuk button invisible; we use our own HTML button */
.ms-nav-masuk-btn {{
    display: inline-flex;
    align-items: center;
    background: #1A9B4B;
    color: #FFFFFF;
    border: none;
    border-radius: 8px;
    padding: 8px 22px;
    font-size: 14px;
    font-weight: 700;
    font-family: 'Inter', Arial, sans-serif;
    cursor: pointer;
    transition: background 0.2s;
}}
.ms-nav-masuk-btn:hover {{ background: #157A3C; }}

/* Hide the hidden login button and its container completely */
div.stButton {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}
div.element-container:has(div.stButton) {{
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}}
</style>
<div class="ms-nav">
    <div class="ms-nav-logo" onclick="window.scrollTo({{top: 0, behavior: 'smooth'}})" style="cursor: pointer;">Mayasih</div>
    <div class="ms-nav-links">
        <span class="ms-nav-link" onclick="document.getElementById('tentang-kami').scrollIntoView({{behavior: 'smooth'}})">Tentang Kami</span>
        <span class="ms-nav-link" onclick="document.getElementById('layanan').scrollIntoView({{behavior: 'smooth'}})">Layanan ▾</span>
        <span class="ms-nav-link" onclick="alert('Fitur Solusi Daur Ulang & Kampus Hijau Mayasih sedang disiapkan!')">Solusi ▾</span>
        <span class="ms-nav-link" onclick="document.getElementById('leaderboard').scrollIntoView({{behavior: 'smooth'}})">Leaderboard</span>
        <span class="ms-nav-link" onclick="alert('Blog & Info Kegiatan Lingkungan Mahasiswa Mayasih akan segera hadir!')">Blog</span>
        <span class="ms-nav-link" onclick="document.getElementById('kontak-kami').scrollIntoView({{behavior: 'smooth'}})">Kontak Kami</span>
    </div>
    <button class="ms-nav-masuk-btn" onclick="(document.querySelector('[data-testid=stBaseButton-nav_login_btn]') || window.parent.document.querySelector('[data-testid=stBaseButton-nav_login_btn]') || document.querySelector('[data-testid=stBaseButton-primary]') || window.parent.document.querySelector('[data-testid=stBaseButton-primary]')).click()">Masuk</button>
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
\"\"\", unsafe_allow_html=True)"""

replacement_nav_hero = """        # ──────────────────────────────────────────
        # 1. NAVIGATION BAR & HERO SECTION — Combined to eliminate layout gaps
        # ──────────────────────────────────────────
        hero_bg_css = f"background-image: url('data:image/png;base64,{hero_b64}'); background-size: cover; background-position: center;" if hero_b64 else "background: var(--ms-green);"
        st.markdown(f\"\"\"
<style>
/* Enable native smooth scroll behavior */
html {{
    scroll-behavior: smooth !important;
}}

/* Style and position the native Streamlit button absolutely over the navbar */
div.element-container:has(button[data-testid="stBaseButton-nav_login_btn"]) {{
    position: fixed !important;
    top: 12px !important;
    right: 60px !important;
    z-index: 10000 !important;
    width: auto !important;
}}

button[data-testid="stBaseButton-nav_login_btn"] {{
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

button[data-testid="stBaseButton-nav_login_btn"]:hover {{
    background-color: #157A3C !important;
    color: #FFFFFF !important;
}}

.ms-nav-link {{
    font-size: 14px;
    font-weight: 500;
    color: #333 !important;
    padding: 6px 18px;
    border-radius: 6px;
    cursor: pointer;
    text-decoration: none !important;
    transition: color 0.2s, background-color 0.2s;
}}
.ms-nav-link:hover {{ color: var(--ms-green) !important; background: var(--ms-green-light) !important; }}
</style>
<div class="ms-nav">
    <a href="#" class="ms-nav-logo" style="text-decoration: none !important;">Mayasih</a>
    <div class="ms-nav-links">
        <a href="#tentang-kami" class="ms-nav-link">Tentang Kami</a>
        <a href="#layanan" class="ms-nav-link">Layanan ▾</a>
        <a href="#" class="ms-nav-link" onclick="alert('Fitur Solusi Daur Ulang & Kampus Hijau Mayasih sedang disiapkan!')">Solusi ▾</a>
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
\"\"\", unsafe_allow_html=True)

        if st.button("Masuk", key="nav_login_btn"):
            st.session_state.show_login = True
            st.session_state.login_role = 'user'
            st.rerun()"""

# 2. Define the CTA block target and replacement
target_cta = """<div class="ms-cta-section">
    <h2 class="ms-cta-title">Satu NIM. Satu Langkah.<br>Kampus Lebih Hijau.</h2>
    <p class="ms-cta-sub">Masuk hanya dengan Nomor Induk Mahasiswa. Mulai laporkan,<br>belajar, dan kumpulkan poin hari ini juga.</p>
    <button class="ms-cta-masuk" onclick="(document.querySelector('[data-testid=stBaseButton-nav_login_btn]') || window.parent.document.querySelector('[data-testid=stBaseButton-nav_login_btn]') || document.querySelector('[data-testid=stBaseButton-primary]') || window.parent.document.querySelector('[data-testid=stBaseButton-primary]')).click()">
        🎓 Masuk dengan NIM
    </button>
</div>"""

replacement_cta = '''<div class="ms-cta-section">
    <h2 class="ms-cta-title">Satu NIM. Satu Langkah.<br>Kampus Lebih Hijau.</h2>
    <p class="ms-cta-sub">Masuk hanya dengan Nomor Induk Mahasiswa. Mulai laporkan,<br>belajar, dan kumpulkan poin hari ini juga.</p>
    <div style="height: 50px;"></div>
</div>
""", unsafe_allow_html=True)

        st.markdown("""
<style>
div.element-container:has(button[data-testid="stBaseButton-cta_login_btn"]) {
    position: relative !important;
    margin-top: -150px !important;
    margin-bottom: 100px !important;
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
    z-index: 10 !important;
    width: 100% !important;
}
button[data-testid="stBaseButton-cta_login_btn"] {
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
}
button[data-testid="stBaseButton-cta_login_btn"]:hover {
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
            st.rerun()'''

# 3. Define the old hidden button at the bottom of the page
target_old_button = """        # Hidden Streamlit button to handle login state trigger via JS click.
        # It is placed at the very bottom of the page to avoid layout gaps.
        if st.button("Masuk", key="nav_login_btn", type="primary"):
            st.session_state.show_login = True
            st.session_state.login_role = 'user'
            st.rerun()"""

# Perform replacements
success = True

# Replace Navbar/Hero
if target_nav_hero in content:
    content = content.replace(target_nav_hero, replacement_nav_hero)
    print("Navbar/Hero target replaced.")
else:
    print("Navbar/Hero target not found.")
    success = False

# Replace CTA
if target_cta in content:
    content = content.replace(target_cta, replacement_cta)
    print("CTA target replaced.")
else:
    print("CTA target not found.")
    success = False

# Replace Old Bottom Button
if target_old_button in content:
    content = content.replace(target_old_button, "")
    print("Old bottom button removed.")
else:
    print("Old bottom button target not found.")

if success:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("All edits successfully written to app.py!")
else:
    print("One or more targets failed. app.py was NOT modified.")
