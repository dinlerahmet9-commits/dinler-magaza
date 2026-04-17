import os
from flask import Flask, render_template_string, request, redirect, session, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dinler_mega_key_2026'
app.config['SESSION_TYPE'] = 'filesystem'

# Veritabanı Yapılandırması
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'dinler_v3.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- VERİTABANI MODELİ ---
class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(100))
    fiyat = db.Column(db.String(20))
    stok = db.Column(db.Integer)
    gorsel = db.Column(db.String(500))

# --- TRENDYOL & SHOPIER TARZI TASARIM (CSS) ---
CSS = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root { --ana-renk: #ff6000; --koyu: #1e1e2d; }
    body { background-color: #f6f9ff; font-family: 'Inter', sans-serif; color: #333; }
    .navbar { background-color: var(--koyu); border-bottom: 3px solid var(--ana-renk); }
    .navbar-brand { font-weight: 800; letter-spacing: 1px; color: white !important; }
    .card { border: none; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); transition: 0.3s; background: white; }
    .card:hover { transform: translateY(-10px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .price-tag { color: var(--ana-renk); font-size: 1.5rem; font-weight: 800; }
    .btn-buy { background: var(--ana-renk); color: white; border-radius: 12px; font-weight: 600; border: none; padding: 12px; }
    .btn-buy:hover { background: #e65600; color: white; }
    .admin-panel { background: white; border-radius: 20px; padding: 30px; margin-top: 30px; }
    .badge-stok { background: #e8fadf; color: #28a745; padding: 5px 12px; border-radius: 8px; font-size: 0.8rem; }
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
        gorsel = u.gorsel if u.gorsel else "https://via.placeholder.com/300x200?text=Urun+Gorseli"
        kartlar += f'''
        <div class="col-lg-3 col-md-6 mb-4">
            <div class="card h-100 overflow-hidden">
                <img src="{gorsel}" class="card-img-top" style="height:200px; object-fit:cover;">
                <div class="card-body">
                    <span class="badge-stok mb-2 d-inline-block">Stokta Var ({u.stok})</span>
                    <h5 class="fw-bold mb-2">{u.ad}</h5>
                    <div class="d-flex justify-content-between align-items-center mt-3">
                        <span class="price-tag">{u.fiyat} TL</span>
                        <button class="btn btn-buy shadow-sm px-4">Al</button>
                    </div>
                </div>
            </div>
        </div>
        '''
    
    return render_template_string(CSS + f"""
    <nav class="navbar navbar-expand-lg navbar-dark p-3">
        <div class="container">
            <a class="navbar-brand" href="/">DİNLER <span style="color:var(--ana-renk)">SATIŞ</span></a>
            <a href="/admin" class="btn btn-outline-light btn-sm rounded-pill"><i class="fa fa-lock me-2"></i>Panel</a>
        </div>
    </nav>
    <div class="container mt-5">
        <div class="d-flex justify-content-between align-items-center mb-5">
            <h2 class="fw-bold m-0 text-dark">Popüler Ürünler</h2>
            <div class="text-muted">Toplam {len(urunler)} ürün listeleniyor</div>
        </div>
        <div class="row">
            {kartlar if urunler else '<div class="col-12 text-center py-5"><i class="fa fa-box-open fa-4x text-muted mb-3"></i><h4>Henüz ürün eklenmedi</h4></div>'}
        </div>
    </div>
    """)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == "dinler16":
            session['auth'] = True
            return redirect(url_for('admin'))
    
    if not session.get('auth'):
        return render_template_string(CSS + """
        <div class="container mt-5">
            <div class="card p-5 shadow mx-auto text-center" style="max-width:450px; border-top: 5px solid #ff6000;">
                <h3 class="fw-bold mb-4">Giriş Yap</h3>
                <form method="POST">
                    <input type="password" name="sifre" class="form-control form-control-lg mb-3 text-center" placeholder="Yönetici Şifresi" autofocus>
                    <button type="submit" class="btn btn-dark btn-lg w-100 shadow">Sisteme Gir</button>
                </form>
            </div>
        </div>
        """)
    
    urunler = Urun.query.all()
    satirlar = ""
    for u in urunler:
        satirlar += f"<tr><td>{u.ad}</td><td><b>{u.fiyat} TL</b></td><td>{u.stok}</td><td><a href='/sil/{u.id}' class='btn btn-sm btn-outline-danger'><i class='fa fa-trash'></i></a></td></tr>"

    return render_template_string(CSS + f"""
    <div class="container mt-4">
        <div class="admin-panel shadow-sm border">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="fw-bold m-0 text-dark">Dinler Satış Paneli</h3>
                <a href="/logout" class="btn btn-danger btn-sm rounded-pill">Güvenli Çıkış</a>
            </div>
            <form action="/ekle" method="POST" class="row g-3 p-3 bg-light rounded-4 mb-5">
                <div class="col-md-4"><label class="small fw-bold">Ürün Adı</label><input name="ad" class="form-control" required></div>
                <div class="col-md-2"><label class="small fw-bold">Fiyat</label><input name="fiyat" class="form-control" required></div>
                <div class="col-md-2"><label class="small fw-bold">Stok</label><input name="stok" type="number" class="form-control" required></div>
                <div class="col-md-4"><label class="small fw-bold">Görsel Linki (Opsiyonel)</label><input name="gorsel" class="form-control" placeholder="https://..."></div>
                <div class="col-12"><button type="submit" class="btn btn-buy w-100 py-3">Ürünü Vitrine Fırlat</button></div>
            </form>
            <h4 class="fw-bold mb-3">Envanter Listesi</h4>
            <div class="table-responsive">
                <table class="table table-hover align-middle">
                    <thead class="table-dark"><tr><th>Ürün</th><th>Fiyat</th><th>Stok</th><th>İşlem</th></tr></thead>
                    <tbody>{satirlar}</tbody>
                </table>
            </div>
        </div>
    </div>
    """)

@app.route('/ekle', methods=['POST'])
def ekle():
    if session.get('auth'):
        yeni = Urun(ad=request.form['ad'], fiyat=request.form['fiyat'], stok=int(request.form['stok']), gorsel=request.form.get('gorsel'))
        db.session.add(yeni)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/sil/<int:id>')
def sil(id):
    if session.get('auth'):
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
