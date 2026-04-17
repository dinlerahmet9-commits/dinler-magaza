import os
from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# ÖNEMLİ: Bu ayarlar oturumun (session) kopmasını engeller
app.config['SECRET_KEY'] = 'dinler_cok_gizli_anahtar_2026'
app.config['SESSION_COOKIE_NAME'] = 'dinler_session'
app.config['SESSION_PERMANENT'] = True

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

# --- TASARIM ---
CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
    body { background-color: #f8f9fa; font-family: sans-serif; }
    .card { border-radius: 15px; border: none; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
</style>
"""

# --- SAYFALAR ---
@app.route('/')
def index():
    try:
        urunler = Urun.query.all()
    except:
        urunler = []
    
    kartlar = ""
    for u in urunler:
        kartlar += f'''
        <div class="col-md-4 mb-4">
            <div class="card p-3 h-100">
                <h5 class="fw-bold">{u.ad}</h5>
                <p class="text-success fs-4 fw-bold">{u.fiyat} TL</p>
                <p class="text-muted small">Stok: {u.stok}</p>
                <button class="btn btn-dark w-100 mt-2">Sipariş Ver</button>
            </div>
        </div>
        '''
    
    return render_template_string(CSS + f"""
    <div class="container mt-5">
        <h1 class="text-center mb-5 fw-bold">DİNLER GLOBAL MAĞAZA</h1>
        <div class="row">
            {kartlar if urunler else '<p class="text-center">Henüz ürün eklenmemiş.</p>'}
        </div>
        <div class="text-center mt-5"><a href="/admin" class="btn btn-sm btn-link text-muted">Yönetici Girişi</a></div>
    </div>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Şifre kontrolü
    if request.method == 'POST':
        if request.form.get('sifre') == "dinler16":
            session['giris_yapti'] = "evet" # Değeri string yaptık (daha garantidir)
            return redirect(url_for('admin'))
    
    # Giriş kontrolü (Eğer oturum yoksa giriş formunu göster)
    if session.get('giris_yapti') != "evet":
        return render_template_string(CSS + """
        <div class="container mt-5 text-center">
            <div class="card p-4 shadow mx-auto" style="max-width:350px;">
                <h4 class="mb-4">Admin Girişi</h4>
                <form method="POST">
                    <input type="password" name="sifre" class="form-control mb-3" placeholder="Şifre" autofocus>
                    <button type="submit" class="btn btn-primary w-100">Giriş Yap</button>
                </form>
            </div>
        </div>
        """)
    
    # Eğer giriş yapılmışsa burası çalışır
    urunler = Urun.query.all()
    satirlar = ""
    for u in urunler:
        satirlar += f"<tr><td>{u.ad}</td><td>{u.fiyat}</td><td>{u.stok}</td><td><a href='/sil/{u.id}' class='btn btn-sm btn-danger'>Sil</a></td></tr>"

    return render_template_string(CSS + f"""
    <div class="container mt-5">
        <div class="card p-4 mb-4">
            <h3>Yeni Ürün Ekle</h3>
            <form action="/ekle" method="POST" class="row g-2">
                <div class="col-md-5"><input name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-3"><input name="fiyat" class="form-control" placeholder="Fiyat" required></div>
                <div class="col-md-2"><input name="stok" type="number" class="form-control" placeholder="Stok" required></div>
                <div class="col-md-2"><button type="submit" class="btn btn-success w-100">Ekle</button></div>
            </form>
        </div>
        <div class="card p-4 text-center">
            <h3>Mevcut Ürünler</h3>
            <table class="table mt-3">
                <thead><tr><th>Ad</th><th>Fiyat</th><th>Stok</th><th>İşlem</th></tr></thead>
                <tbody>{satirlar}</tbody>
            </table>
            <a href="/logout" class="btn btn-link text-danger mt-3">Güvenli Çıkış</a>
        </div>
    </div>
    """)

@app.route('/ekle', methods=['POST'])
def ekle():
    if session.get('giris_yapti') == "evet":
        yeni = Urun(ad=request.form['ad'], fiyat=request.form['fiyat'], stok=int(request.form['stok']))
        db.session.add(yeni)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/sil/<int:id>')
def sil(id):
    if session.get('giris_yapti') == "evet":
        u = Urun.query.get(id)
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
