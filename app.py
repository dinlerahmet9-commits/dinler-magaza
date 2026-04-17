import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# Güvenlik anahtarı
app.secret_key = os.environ.get('SECRET_KEY', 'dinler_gizli_anahtar_123')

# Veritabanı yolu ayarı
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dukkan.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- VERİTABANI MODELLERİ ---
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    fiyat = db.Column(db.Float)
    stok = db.Column(db.Integer)

class Siparis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    urun_ad = db.Column(db.String(100))
    musteri = db.Column(db.String(100))
    tarih = db.Column(db.DateTime, default=datetime.now)

# --- TASARIM ---
HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <title>Dinler Satış</title>
</head>
<body class="bg-light">
    <nav class="navbar navbar-dark bg-dark mb-4">
        <div class="container"><a class="navbar-brand" href="/">🛒 DİNLER GLOBAL SATIŞ</a></div>
    </nav>
    <div class="container text-center">
        <h2 class="mb-4">🚀 Sitemiz Aktif!</h2>
        <div class="row">
            {% if not urunler %}
                <p class="lead">Henüz ürün eklenmemiş. Yönetici panelinden ürün ekleyebilirsiniz.</p>
            {% endif %}
            {% for urun in urunler %}
            <div class="col-md-4">
                <div class="card mb-3 shadow-sm text-start">
                    <div class="card-body">
                        <h5>{{ urun.ad }}</h5>
                        <p class="fw-bold text-primary">{{ urun.fiyat }} TL</p>
                        <p>Stok: {{ urun.stok }}</p>
                        <button class="btn btn-outline-dark btn-sm w-100">Sipariş Ver</button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        urunler = Urun.query.all()
    except:
        urunler = []
    return render_template_string(HTML, urunler=urunler)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
