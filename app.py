import os
from flask import Flask, render_template_string, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dinler_premium_2026_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dinler_kurumsal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- VERİTABANI MODELLERİ ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.String(100))

class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200))
    fiyat = db.Column(db.String(50))
    stok = db.Column(db.Integer)
    gorsel = db.Column(db.String(500))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- PROFESYONEL TASARIM (CSS) ---
DESIGN = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
    body { font-family: 'Poppins', sans-serif; background-color: #f4f6f9; }
    .navbar { background: #ffffff; border-bottom: 1px solid #eee; padding: 15px 0; }
    .navbar-brand { font-weight: 700; color: #ff6000 !important; font-size: 24px; }
    .hero-section { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 60px 0; border-radius: 0 0 50px 50px; }
    .card-product { border: none; border-radius: 20px; transition: 0.4s; background: #fff; overflow: hidden; height: 100%; }
    .card-product:hover { transform: translateY(-10px); box-shadow: 0 20px 40px rgba(0,0,0,0.08); }
    .price { color: #ff6000; font-weight: 700; font-size: 20px; }
    .btn-cart { background: #ff6000; color: white; border-radius: 10px; border: none; padding: 10px 20px; font-weight: 600; width: 100%; }
    .btn-cart:hover { background: #e65600; color: white; }
    .admin-card { background: white; border-radius: 20px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.05); }
</style>
"""

# --- SAYFA FONKSİYONLARI ---
@app.route('/')
def index():
    urunler = Urun.query.all()
    kartlar = ""
    for u in urunler:
        img = u.gorsel if u.gorsel else "https://via.placeholder.com/400x400.png?text=Dinler+Satis"
        kartlar += f'''
        <div class="col-lg-3 col-md-4 col-6 mb-4">
            <div class="card-product shadow-sm">
                <img src="{img}" class="card-img-top" style="height:250px; object-fit:cover;">
                <div class="card-body">
                    <h6 class="text-muted mb-1 text-uppercase small">Dinler Global</h6>
                    <h5 class="fw-bold mb-2" style="font-size:16px;">{u.ad}</h5>
                    <div class="price mb-3 text-center">{u.fiyat} TL</div>
                    <button class="btn-cart shadow-sm">Sepete Ekle</button>
                </div>
            </div>
        </div>
        '''
    
    return render_template_string(DESIGN + f"""
    <nav class="navbar navbar-expand-lg sticky-top">
        <div class="container">
            <a class="navbar-brand" href="/">DİNLER <span style="color:#333">SATIŞ</span></a>
            <div class="d-flex align-items-center">
                <a href="/login" class="btn btn-outline-dark btn-sm rounded-pill px-4">Yönetici</a>
            </div>
        </div>
    </nav>
    <div class="hero-section text-center mb-5">
        <div class="container">
            <h1 class="display-4 fw-bold">Yeni Nesil Alışveriş</h1>
            <p class="lead opacity-75">Dinler Satış Paneli ile güvenli ve hızlı ticaret.</p>
        </div>
    </div>
    <div class="container pb-5">
        <div class="row">{kartlar if urunler else '<h4 class="text-center text-muted">Vitrinimiz hazırlanıyor...</h4>'}</div>
    </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('password') == 'dinler16':
            user = User.query.first()
            login_user(user)
            return redirect(url_for('admin'))
    return render_template_string(DESIGN + """
    <div class="container mt-5 pt-5">
        <div class="admin-card mx-auto" style="max-width:400px;">
            <h3 class="text-center fw-bold mb-4">Yönetici Girişi</h3>
            <form method="POST">
                <input type="password" name="password" class="form-control form-control-lg mb-3 rounded-4" placeholder="Şifre" required>
                <button type="submit" class="btn btn-dark btn-lg w-100 rounded-4">Giriş Yap</button>
            </form>
        </div>
    </div>
    """)

@app.route('/admin')
@login_required
def admin():
    urunler = Urun.query.all()
    satirlar = ""
    for u in urunler:
        satirlar += f"<tr><td>{u.ad}</td><td>{u.fiyat} TL</td><td>{u.stok}</td><td><a href='/delete/{u.id}' class='btn btn-danger btn-sm'>Sil</a></td></tr>"
    
    return render_template_string(DESIGN + f"""
    <div class="container mt-5">
        <div class="admin-card">
            <div class="d-flex justify-content-between mb-4">
                <h2 class="fw-bold">Mağaza Yönetimi</h2>
                <a href="/logout" class="btn btn-outline-danger">Çıkış</a>
            </div>
            <form action="/add" method="POST" class="row g-3 mb-5 border p-3 rounded-4 bg-light">
                <div class="col-md-4"><input name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-2"><input name="fiyat" class="form-control" placeholder="Fiyat (1.500)" required></div>
                <div class="col-md-2"><input name="stok" type="number" class="form-control" placeholder="Stok" required></div>
                <div class="col-md-4"><input name="gorsel" class="form-control" placeholder="Resim Linki"></div>
                <div class="col-12"><button class="btn btn-success w-100 shadow-sm py-2">Ürünü Yayınla</button></div>
            </form>
            <table class="table table-hover">
                <thead><tr><th>Ürün</th><th>Fiyat</th><th>Stok</th><th>İşlem</th></tr></thead>
                <tbody>{satirlar}</tbody>
            </table>
        </div>
    </div>
    """)

@app.route('/add', methods=['POST'])
@login_required
def add():
    yeni = Urun(ad=request.form['ad'], fiyat=request.form['fiyat'], stok=int(request.form['stok']), gorsel=request.form.get('gorsel'))
    db.session.add(yeni)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    u = Urun.query.get(id)
    db.session.delete(u)
    db.session.commit()
    return redirect(url_for('admin'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if not User.query.first():
            db.session.add(User(password='dinler16'))
            db.session.commit()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
