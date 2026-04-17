import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Gizli anahtarı daha güvenli hale getirdik
app.secret_key = os.environ.get('SECRET_KEY', 'dinler_123456789')

# Veritabanı yapılandırması
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dukkan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- YÖNETİCİ ŞİFRESİ ---
ADMIN_PASS = "dinler16"

# --- MODELLER ---
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    stok = db.Column(db.Integer, default=0)

# --- TASARIM (TEK PARÇA HTML) ---
def get_layout(content):
    return f"""
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body {{ background-color: #f8f9fa; }}
            .navbar {{ background-color: #212529 !important; }}
            .card {{ border: none; border-radius: 10px; transition: 0.3s; }}
            .card:hover {{ box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        </style>
        <title>Dinler Satış</title>
    </head>
    <body>
        <nav class="navbar navbar-dark mb-4 shadow-sm">
            <div class="container">
                <a class="navbar-brand fw-bold" href="/">🛒 DİNLER GLOBAL</a>
                <a href="/admin" class="btn btn-outline-light btn-sm">Yönetici Paneli</a>
            </div>
        </nav>
        <div class="container">{content}</div>
    </body>
    </html>
    """

# --- YOLLAR ---
@app.route('/')
def index():
    try:
        urunler = Urun.query.all()
    except:
        urunler = []
    
    content = '<div class="row">'
    if not urunler:
        content += '<div class="col-12 text-center text-muted mt-5"><h5>Henüz ürün eklenmemiş.</h5></div>'
    for u in urunler:
        content += f"""
        <div class="col-md-4 mb-4">
            <div class="card shadow-sm h-100 p-3">
                <h5>{u.ad}</h5>
                <p class="text-primary fw-bold fs-4">{u.fiyat} TL</p>
                <p class="text-muted small">Stok: {u.stok} adet</p>
                <button class="btn btn-dark w-100">Sipariş Ver</button>
            </div>
        </div>
        """
    content += '</div>'
    return render_template_string(get_layout(content))

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == ADMIN_PASS:
            session['admin_logged_in'] = True
            return redirect(url_for('admin'))
    
    if not session.get('admin_logged_in'):
        login_form = """
        <div class="row justify-content-center mt-5">
            <div class="col-md-4 card p-4 shadow">
                <form method="POST text-center">
                    <h5 class="mb-3">Panel Girişi</h5>
                    <input type="password" name="sifre" class="form-control mb-3" placeholder="Yönetici Şifresi">
                    <button class="btn btn-primary w-100">Giriş Yap</button>
                </form>
            </div>
        </div>
        """
        return render_template_string(get_layout(login_form))
    
    # Yönetici içerik
    urunler = Urun.query.all()
    admin_content = f"""
    <div class="card p-4 shadow-sm mb-4">
        <h4>Yeni Ürün Ekle</h4>
        <form action="/admin/ekle" method="POST" class="row g-3">
            <div class="col-md-6"><input type="text" name="ad" class="form-control" placeholder="Ürün Adı" required></div>
            <div class="col-md-3"><input type="number" step="0.01" name="fiyat" class="form-control" placeholder="Fiyat" required></div>
            <div class="col-md-3"><input type="number" name="stok" class="form-control" placeholder="Stok" required></div>
            <div class="col-12"><button class="btn btn-success w-100">Ekle</button></div>
        </form>
    </div>
    <div class="card p-4 shadow-sm text-center">
        <h4>Mevcut Stoklar</h4>
        <table class="table mt-3">
            <thead><tr><th>Ürün</th><th>Fiyat</th><th>Stok</th></tr></thead>
            <tbody>
    """
    for u in urunler:
        admin_content += f"<tr><td>{u.ad}</td><td>{u.fiyat} TL</td><td>{u.stok}</td></tr>"
    
    admin_content += "</tbody></table><a href='/logout' class='btn btn-link text-danger mt-3'>Çıkış Yap</a></div>"
    return render_template_string(get_layout(admin_content))

@app.route('/admin/ekle', methods=['POST'])
def ekle():
    if session.get('admin_logged_in'):
        try:
            ad = request.form.get('ad')
            fiyat = float(request.form.get('fiyat'))
            stok = int(request.form.get('stok'))
            yeni = Urun(ad=ad, fiyat=fiyat, stok=stok)
            db.session.add(yeni)
            db.session.commit()
        except:
            db.session.rollback()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
