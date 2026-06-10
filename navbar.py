import os

filepath = r"c:\Users\muhda\Downloads\Tubes Algoritma\app.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Define target block containing the navbar stylesheet and elements (using the updated "Layanan v" and "Solusi v")
target_nav_hero_style = """<style>
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
    <a href="#" class="ms-nav-logo" style="text-decoration: none !important;">Mayasih</a>"""

replacement_nav_hero_style = """<style>
/* Enable native smooth scroll behavior */
html {{
    scroll-behavior: smooth !important;
}}

/* Position the native Streamlit button absolutely over the navbar directly */
button[data-testid="stBaseButton-nav_login_btn"] {{
    position: fixed !important;
    top: 12px !important;
    right: 60px !important;
    z-index: 10000 !important;
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

/* Style the logo to prevent default link coloring and underlines */
.ms-nav-logo {{
    display: inline-block !important;
    font-size: 22px !important;
    font-weight: 800 !important;
    color: #1A9B4B !important;
    letter-spacing: -0.5px !important;
    text-decoration: none !important;
}}

/* Style links as inline-blocks to respect padding and hover background */
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
    <a href="#" class="ms-nav-logo">Mayasih</a>"""

# 2. Update the CTA style block to target the button directly without :has()
target_cta_style = """        st.markdown(\"\"\"
<style>
div.element-container:has(button[data-testid="stBaseButton-cta_login_btn"]) {{
    position: relative !important;
    margin-top: -150px !important;
    margin-bottom: 100px !important;
    text-align: center !important;
    display: flex !important;
    justify-content: center !important;
    z-index: 10 !important;
    width: 100% !important;
}}
button[data-testid="stBaseButton-cta_login_btn"] {{
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
}}
button[data-testid="stBaseButton-cta_login_btn"]:hover {{
    background-color: #FFFFFF !important;
    color: #1A9B4B !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.2) !important;
}}
</style>
\"\"\", unsafe_allow_html=True)"""

replacement_cta_style = """        st.markdown(\"\"\"
<style>
/* Position cta_login_btn directly and pull it up using margin-top */
button[data-testid="stBaseButton-cta_login_btn"] {{
    display: block !important;
    margin: -150px auto 100px auto !important;
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
    z-index: 10 !important;
}}
button[data-testid="stBaseButton-cta_login_btn"]:hover {{
    background-color: #FFFFFF !important;
    color: #1A9B4B !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 28px rgba(0,0,0,0.2) !important;
}}
</style>
\"\"\", unsafe_allow_html=True)"""

success = True

if target_nav_hero_style in content:
    content = content.replace(target_nav_hero_style, replacement_nav_hero_style)
    print("Navbar style updated.")
else:
    print("Navbar style target not found.")
    success = False

if target_cta_style in content:
    content = content.replace(target_cta_style, replacement_cta_style)
    print("CTA style updated.")
else:
    print("CTA style target not found.")
    success = False

if success:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print("All styling edits written to app.py successfully!")
else:
    print("Styling edits failed.")
