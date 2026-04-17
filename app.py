import os
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = 'dinler_final_key_2026'

# --- TASARIM (CSS) ---
CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    :root { --main: #ff6000; }
    body { background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
    .navbar { background: #1a1a1a; border-bottom: 3px solid var(--main); }
    .product-card { border: none; border-radius: 15px; transition: 0.3s; background: white; }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .btn-main { background: var(--main); color: white; border: none; border-radius: 8px; font-weight: 600; }
</style>
"""

# --- BASİT VERİ SAKLAMA (Hata Almamak İçin Şimdilik Liste) ---
urunler = []

@app.route('/')
def index():
    kartlar = ""
    for idx, u in enumerate(urunler):
        kartlar += f'''
        <div class="col-md-4 mb-4">
            <div class="product-card p-3 shadow-sm">
                <img src="https://via.placeholder.com/300x200?text=Dinler+Satis" class="w-100 rounded mb-3">
                <h5 class="fw-bold">{u['ad']}</h5>
                <p class="text-orange fs-4 fw-bold" style="color:var(--main)">{u['fiyat']} TL</p>
                <button class="btn btn-dark w-100">Sepete Ekle</button>
            </div>
        </div>
        '''
    return render_template_string(CSS + f"""
    <nav class="navbar navbar-dark p-3 shadow">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">DİNLER <span style="color:var(--main)">SATIŞ</span></a>
            <a href="/admin" class="btn btn-outline-light btn-sm">Panel</a>
        </div>
    </nav>
    <div class="container mt-5">
        <div class="row">{kartlar if urunler else '<h4 class="text-center text-muted">Vitrin henüz boş. Admin panelinden ürün ekleyin!</h4>'}</div>
    </div>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == 'dinler16':
            session['giris'] = True
            return redirect('/admin')
    
    if not session.get('giris'):
        return render_template_string(CSS + """
        <div class="container mt-5 text-center">
            <div class="card p-4 shadow mx-auto" style="max-width:350px;">
                <h3>Admin Girişi</h3>
                <form method="POST"><input type="password" name="sifre" class="form-control mb-3" placeholder="Şifre">
                <button class="btn btn-main w-100">Giriş Yap</button></form>
            </div>
        </div>
        """)
    
    return render_template_string(CSS + """
    <div class="container mt-5">
        <div class="card p-4 shadow">
            <h3>Ürün Ekle</h3>
            <form action="/ekle" method="POST" class="row g-3">
                <div class="col-md-6"><input name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-4"><input name="fiyat" class="form-control" placeholder="Fiyat" required></div>
                <div class="col-md-2"><button class="btn btn-success w-100">Ekle</button></div>
            </form>
            <hr>
            <a href="/logout" class="btn btn-link text-danger">Çıkış Yap</a>
        </div>
    </div>
    """)

@app.route('/ekle', methods=['POST'])
def ekle():
    if session.get('giris'):
        urunler.append({'ad': request.form['ad'], 'fiyat': request.form['fiyat']})
    return redirect('/')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
import os
from flask import Flask, render_template_string, request, redirect

app = Flask(__name__)

# --- ULTRA MODERN TASARIM ---
CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    :root { --main: #ff6000; }
    body { background: #f8f9fa; font-family: 'Segoe UI', sans-serif; }
    .navbar { background: #1a1a1a; border-bottom: 3px solid var(--main); }
    .product-card { border: none; border-radius: 15px; background: white; transition: 0.3s; }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .btn-main { background: var(--main); color: white; border-radius: 8px; font-weight: 600; border: none; }
</style>
"""

# ÜRÜNLERİ HAFIZADA TUTALIM
urunler = []

@app.route('/')
def index():
    kartlar = ""
    for u in urunler:
        img = u['gorsel'] if u['gorsel'] else "https://via.placeholder.com/300x200?text=Urun"
        kartlar += f'''
        <div class="col-md-4 mb-4">
            <div class="product-card p-3 shadow-sm text-center">
                <img src="{img}" class="w-100 rounded mb-3" style="height:200px; object-fit:cover;">
                <h5 class="fw-bold">{u['ad']}</h5>
                <p class="text-orange fs-4 fw-bold" style="color:var(--main)">{u['fiyat']} TL</p>
                <button class="btn btn-dark w-100">Satın Al</button>
            </div>
        </div>
        '''
    return render_template_string(CSS + f"""
    <nav class="navbar navbar-dark p-3">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">DİNLER <span style="color:var(--main)">SATIŞ</span></a>
        </div>
    </nav>
    <div class="container mt-5">
        <h2 class="mb-4 fw-bold text-center text-dark">Mağaza Vitrini</h2>
        <div class="row">{kartlar if urunler else '<h4 class="text-center text-muted py-5">Vitrin şu an boş.</h4>'}</div>
    </div>
    """)

# --- GİZLİ GİRİŞ PANELİ ---
# Buraya sadece 'siteniz.com/admin/dinler16' yazanlar girebilir.
@app.route('/admin/dinler16')
def admin_paneli():
    satirlar = ""
    for idx, u in enumerate(urunler):
        satirlar += f"<tr><td>{u['ad']}</td><td>{u['fiyat']} TL</td></tr>"
        
    return render_template_string(CSS + f"""
    <div class="container mt-5">
        <div class="card p-4 shadow border-0">
            <h2 class="fw-bold text-success mb-4">Hoş Geldin Kanka! (Admin Aktif)</h2>
            <form action="/ekle" method="POST" class="row g-3">
                <div class="col-md-5"><input name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-2"><input name="fiyat" class="form-control" placeholder="Fiyat" required></div>
                <div class="col-md-3"><input name="gorsel" class="form-control" placeholder="Resim Linki"></div>
                <div class="col-md-2"><button class="btn btn-main w-100">Ürünü Ekle</button></div>
            </form>
            <hr>
            <h4 class="mt-4">Eklenen Ürünler</h4>
            <table class="table mt-2"><thead><tr><th>Ad</th><th>Fiyat</th></tr></thead><tbody>{satirlar}</tbody></table>
            <a href="/" class="btn btn-link mt-3">Siteden Çıkış Yap / Vitrine Dön</a>
        </div>
    </div>
    """)

@app.route('/ekle', methods=['POST'])
def ekle():
    yeni_urun = {
        'ad': request.form['ad'],
        'fiyat': request.form['fiyat'],
        'gorsel': request.form.get('gorsel')
    }
    urunler.append(yeni_urun)
    return redirect('/admin/dinler16')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
