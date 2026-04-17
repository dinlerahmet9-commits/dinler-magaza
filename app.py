import os
from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "dinler_cok_ozel_anahtar_2026"

# Veritabanı Ayarı
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dukkan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- VERİTABANI MODELİ ---
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    fiyat = db.Column(db.String(20))
    stok = db.Column(db.Integer)

# --- TASARIM (MODERN VE ŞIK) ---
CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f4f7f6; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .navbar { background: linear-gradient(90deg, #1a1a1a, #4a4a4a); box-shadow: 0 2px 10px rgba(0,0,0,0.2); }
    .card { border: none; border-radius: 15px; transition: transform 0.3s; }
    .card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .admin-btn { position: fixed; bottom: 20px; right: 20px; border-radius: 50px; padding: 10px 20px; }
</style>
"""

# --- SAYFALAR ---
@app.route('/')
def index():
    urunler = Urun.query.all()
    urun_kartlari = ""
    for u in urunler:
        urun_kartlari += f'''
        <div class="col-md-4 mb-4">
            <div class="card p-3 shadow-sm h-100">
                <h5 class="fw-bold">{u.ad}</h5>
                <p class="text-primary fs-4 fw-bold mb-1">{u.fiyat} TL</p>
                <p class="text-muted small">Stok: {u.stok} adet</p>
                <button class="btn btn-dark w-100 mt-2 rounded-pill">Sipariş Ver</button>
            </div>
        </div>
        '''
    
    icerik = f"""
    <div class="container mt-5 text-center">
        <h1 class="display-5 fw-bold mb-4">DİNLER GLOBAL MAĞAZA</h1>
        <div class="row">
            {urun_kartlari if urunler else '<p class="lead mt-5">Ürünlerimiz yakında burada sergilenecek.</p>'}
        </div>
        <a href="/admin" class="btn btn-outline-secondary btn-sm admin-btn shadow">Yönetici Girişi</a>
    </div>
    """
    return render_template_string(CSS + icerik)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == "dinler16":
            session['admin_giris'] = True
            return redirect(url_for('admin'))
    
    if not session.get('admin_giris'):
        return render_template_string(CSS + """
        <div class="container mt-5">
            <div class="card p-4 shadow-sm mx-auto" style="max-width:400px;">
                <h4 class="text-center mb-4">Panel Girişi</h4>
                <form method="POST">
                    <input type="password" name="sifre" class="form-control mb-3" placeholder="Şifrenizi Girin">
                    <button type="submit" class="btn btn-primary w-100">Giriş Yap</button>
                </form>
                <a href="/" class="d-block text-center mt-3 text-decoration-none text-muted">← Mağazaya Dön</a>
            </div>
        </div>
        """)
    
    # Giriş yapılmışsa Admin Paneli içeriği
    urunler = Urun.query.all()
    tablo_satirlari = ""
    for u in urunler:
        tablo_satirlari += f"<tr><td>{u.ad}</td><td>{u.fiyat} TL</td><td>{u.stok}</td><td><a href='/sil/{u.id}' class='btn btn-danger btn-sm'>Sil</a></td></tr>"

    admin_icerik = f"""
    <div class="container mt-5">
        <div class="card p-4 shadow-sm mb-4">
            <h3>Yeni Ürün Ekle</h3>
            <form action="/ekle" method="POST" class="row g-3">
                <div class="col-md-6"><input type="text" name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-3"><input type="text" name="fiyat" class="form-control" placeholder="Fiyat (Örn: 150.00)" required></div>
                <div class="col-md-3"><input type="number" name="stok" class="form-control" placeholder="Stok Adedi" required></div>
                <div class="col-12"><button type="submit" class="btn btn-success w-100">Ürünü Vitrine Ekle</button></div>
            </form>
        </div>
        <div class="card p-4 shadow-sm">
            <h3>Mevcut Ürünler</h3>
            <table class="table mt-3">
                <thead><tr><th>Ad</th><th>Fiyat</th><th>Stok</th><th>İşlem</th></tr></thead>
                <tbody>{tablo_satirlari}</tbody>
            </table>
            <a href="/logout" class="btn btn-link text-danger">Güvenli Çıkış</a>
        </div>
    </div>
    """
    return render_template_string(CSS + admin_icerik)

@app.route('/ekle', methods=['POST'])
def ekle():
    if session.get('admin_giris'):
        yeni_urun = Urun(ad=request.form['ad'], fiyat=request.form['fiyat'], stok=int(request.form['stok']))
        db.session.add(yeni_urun)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/sil/<int:id>')
def sil(id):
    if session.get('admin_giris'):
        urun = Urun.query.get(id)
        db.session.delete(urun)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_giris', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
