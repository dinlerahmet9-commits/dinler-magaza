import os
from flask import Flask, render_template_string

app = Flask(__name__)

# Tasarım
HTML = """
<!DOCTYPE html>
<html>
<head><title>Dinler Satis</title></head>
<body style="text-align:center; padding-top:50px; font-family:sans-serif;">
    <h1>🚀 DİNLER SATIŞ SİTESİ CANLI!</h1>
    <p>Sunucu bağlantısı başarıyla sağlandı.</p>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)import os
from flask import Flask, render_template_string, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
# İnternette çalışması için gizli anahtar
app.secret_key = os.environ.get('SECRET_KEY', 'dinler_gizli_anahtar_123')

# Veritabanı yolu (İnternet sunucularına uygun hale getirildi)
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

# --- TASARIM (BASİT VE ŞIK) ---
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
        <h2>Hoş Geldiniz</h2>
        <p class="lead">Ürünlerimiz yakında burada sergilenecek.</p>
        <div class="row">
            {% for urun in urunler %}
            <div class="col-md-4">
                <div class="card mb-3 shadow-sm">
                    <div class="card-body">
                        <h5>{{ urun.ad }}</h5>
                        <p class="fw-bold text-primary">{{ urun.fiyat }} TL</p>
                        <p>Stok: {{ urun.stok }}</p>
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
    urunler = Urun.query.all()
    return render_template_string(HTML, urunler=urunler)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # İnternet sunucuları genelde 5000 yerine bu ayarı bekler
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
