import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dinler_ozel_anahtar_2026' # Güvenlik için

# Veritabanı yolu
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dukkan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- YÖNETİCİ ŞİFRESİ ---
ADMIN_PASS = "dinler16" # Panele girmek için kullanacağınız şifre

# --- MODELLER ---
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    fiyat = db.Column(db.Float)
    stok = db.Column(db.Integer)

# --- TASARIM (HTML) ---
LAYOUT = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Dinler Global Satış</title>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container">
            <a class="navbar-brand" href="/">🛒 DİNLER GLOBAL</a>
            <a href="/admin" class="btn btn-outline-light btn-sm">Yönetici Paneli</a>
        </div>
    </nav>
    <div class="container">
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

VITRIN_HTML = """
{% extends "layout" %}
{% block content %}
<div class="text-center">
    <h2 class="mb-4">Ürün Katalogu</h2>
    <div class="row">
        {% if not urunler %}
            <div class="alert alert-info">Dükkan henüz hazırlık aşamasında, çok yakında buradayız!</div>
        {% endif %}
        {% for urun in urunler %}
        <div class="col-md-4 mb-4">
            <div class="card h-100 shadow-sm">
                <div class="card-body text-start">
                    <h5>{{ urun.ad }}</h5>
                    <p class="text-primary fw-bold fs-5">{{ urun.fiyat }} TL</p>
                    <p class="text-muted">Mevcut Stok: {{ urun.stok }}</p>
                    <button class="btn btn-dark w-100 mt-2">Satın Al</button>
                </div>
            </div>
        </div>
        {% endfor %}
    </div>
</div>
{% endblock %}
"""

ADMIN_HTML = """
{% extends "layout" %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card p-4 mb-4 shadow border-0">
            <h3>Yeni Ürün Ekle</h3>
            <form action="/admin/ekle" method="POST" class="row g-3">
                <div class="col-md-6"><input type="text" name="ad" placeholder="Ürün Adı" class="form-control" required></div>
                <div class="col-md-3"><input type="number" step="0.01" name="fiyat" placeholder="Fiyat" class="form-control" required></div>
                <div class="col-md-3"><input type="number" name="stok" placeholder="Stok" class="form-control" required></div>
                <div class="col-12"><button class="btn btn-success w-100">Dükkana Kaydet</button></div>
            </form>
        </div>
        
        <div class="card p-4 shadow border-0">
            <h3>Mevcut Stoklar</h3>
            <table class="table">
                <thead><tr><th>Ürün</th><th>Fiyat</th><th>Stok</th><th>İşlem</th></tr></thead>
                <tbody>
                    {% for urun in urunler %}
                    <tr>
                        <td>{{ urun.ad }}</td><td>{{ urun.fiyat }} TL</td><td>{{ urun.stok }}</td>
                        <td><a href="/admin/sil/{{ urun.id }}" class="text-danger">Sil</a></td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
{% endblock %}
"""

# --- YOLLAR ---
@app.route('/')
def index():
    urunler = Urun.query.all()
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', VITRIN_HTML), urunler=urunler)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == ADMIN_PASS:
            session['admin'] = True
            return redirect('/admin')
    
    if not session.get('admin'):
        return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', """
            <div class="text-center mt-5">
                <form method="POST" style="max-width:300px; margin:auto;">
                    <h4>Yönetici Girişi</h4>
                    <input type="password" name="sifre" class="form-control mb-2" placeholder="Şifre">
                    <button class="btn btn-primary w-100">Giriş</button>
                </form>
            </div>
        """))
    
    urunler = Urun.query.all()
    return render_template_string(LAYOUT.replace('{% block content %}{% endblock %}', ADMIN_HTML), urunler=urunler)

@app.route('/admin/ekle', methods=['POST'])
def ekle():
    if session.get('admin'):
        yeni = Urun(ad=request.form['ad'], fiyat=float(request.form['fiyat']), stok=int(request.form['stok']))
        db.session.add(yeni)
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/sil/<int:id>')
def sil(id):
    if session.get('admin'):
        urun = Urun.query.get(id)
        db.session.delete(urun)
        db.session.commit()
    return redirect('/admin')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
