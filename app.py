import os
from flask import Flask, render_template_string, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dinler_mega_platform_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dinler_pazar.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- MODELLER ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='buyer') # 'buyer' veya 'seller'
    guvenlik_sorusu = db.Column(db.String(200))
    guvenlik_cevabi = db.Column(db.String(200))

class Urun(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ad = db.Column(db.String(200), nullable=False)
    fiyat = db.Column(db.Float, nullable=False)
    kategori = db.Column(db.String(50))
    gorsel = db.Column(db.String(500))
    satici_id = db.Column(db.Integer, db.ForeignKey('user.id'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- TASARIM SİSTEMİ (CSS) ---
DESIGN = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root { --main: #ff6000; --dark: #1e1e2d; }
    body { background: #f4f6f9; font-family: 'Poppins', sans-serif; }
    .navbar { background: white; border-bottom: 2px solid var(--main); }
    .nav-link { color: var(--dark) !important; font-weight: 500; }
    .btn-main { background: var(--main); color: white; border-radius: 8px; border: none; }
    .btn-main:hover { background: #e65600; color: white; }
    .search-bar { border-radius: 20px 0 0 20px; border: 1px solid #ddd; }
    .search-btn { border-radius: 0 20px 20px 0; background: var(--main); color: white; border: none; }
    .product-card { border: none; border-radius: 15px; transition: 0.3s; background: white; }
    .product-card:hover { transform: translateY(-5px); box-shadow: 0 10px 20px rgba(0,0,0,0.1); }
    .sidebar { background: white; border-radius: 15px; padding: 20px; }
</style>
"""

# --- ORTAK NAVBAR ---
def get_nav():
    auth_links = ""
    if current_user.is_authenticated:
        panel_link = url_for('seller_panel') if current_user.role == 'seller' else url_for('buyer_panel')
        auth_links = f'''
            <li class="nav-item"><a class="nav-link" href="{panel_link} text-primary fw-bold">Panelim</a></li>
            <li class="nav-item"><a class="nav-link text-danger" href="/logout">Çıkış</a></li>
        '''
    else:
        auth_links = '''
            <li class="nav-item"><a class="nav-link" href="/login">Giriş Yap</a></li>
            <li class="nav-item"><a class="btn btn-main btn-sm px-3 ms-2" href="/register">Hesap Aç</a></li>
        '''
    
    return f'''
    <nav class="navbar navbar-expand-lg sticky-top mb-4">
        <div class="container">
            <a class="navbar-brand fw-bold" href="/">DİNLER <span style="color:var(--main)">SATIŞ</span></a>
            <form class="d-flex mx-auto w-50" action="/" method="GET">
                <input class="form-control search-bar" name="q" type="search" placeholder="Ürün veya kategori ara...">
                <button class="search-btn px-3" type="submit"><i class="fa fa-search"></i></button>
            </form>
            <ul class="navbar-nav ms-auto align-items-center">{auth_links}</ul>
        </div>
    </nav>
    '''

# --- YOLLAR ---

@app.route('/')
def index():
    query = request.args.get('q', '')
    kat = request.args.get('kat', '')
    
    urun_query = Urun.query
    if query:
        urun_query = urun_query.filter(Urun.ad.contains(query) | Urun.kategori.contains(query))
    if kat:
        urun_query = urun_query.filter_by(kategori=kat)
    
    urunler = urun_query.all()
    
    kartlar = ""
    for u in urunler:
        img = u.gorsel if u.gorsel else "https://via.placeholder.com/300x300?text=Urun"
        kartlar += f'''
        <div class="col-md-4 mb-4">
            <div class="product-card shadow-sm p-3 h-100">
                <img src="{img}" class="img-fluid rounded mb-3" style="height:200px; width:100%; object-fit:cover;">
                <h6 class="text-muted small">{u.kategori}</h6>
                <h5 class="fw-bold">{u.ad}</h5>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="fs-4 fw-bold text-main" style="color:var(--main)">{u.fiyat} TL</span>
                    <button class="btn btn-dark btn-sm rounded-pill px-3">Sepete Ekle</button>
                </div>
            </div>
        </div>
        '''

    return render_template_string(DESIGN + get_nav() + f"""
    <div class="container">
        <div class="row">
            <div class="col-md-3">
                <div class="sidebar shadow-sm">
                    <h5 class="fw-bold mb-3">Kategoriler</h5>
                    <ul class="list-unstyled">
                        <li><a href="/" class="text-decoration-none text-dark">Tümü</a></li>
                        <li><a href="/?kat=Elektronik" class="text-decoration-none text-dark">Elektronik</a></li>
                        <li><a href="/?kat=Giyim" class="text-decoration-none text-dark">Giyim</a></li>
                        <li><a href="/?kat=Ev-Yasam" class="text-decoration-none text-dark">Ev & Yaşam</a></li>
                    </ul>
                </div>
            </div>
            <div class="col-md-9">
                <div class="row">{kartlar if urunler else '<p class="text-center mt-5">Aradığınız kriterde ürün bulunamadı.</p>'}</div>
            </div>
        </div>
    </div>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(
            username=request.form['username'], 
            password=hashed_pw,
            role=request.form['role'],
            guvenlik_sorusu="En sevdiğiniz renk nedir?",
            guvenlik_cevabi=request.form['guvenlik'].lower()
        )
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    
    return render_template_string(DESIGN + """
    <div class="container mt-5"><div class="card p-5 mx-auto shadow-lg" style="max-width:500px;">
        <h2 class="fw-bold text-center mb-4">Hesap Oluştur</h2>
        <form method="POST">
            <input name="username" class="form-control mb-3" placeholder="Kullanıcı Adı" required>
            <input name="password" type="password" class="form-control mb-3" placeholder="Şifre" required>
            <select name="role" class="form-select mb-3">
                <option value="buyer">Alıcıyım (Alışveriş yapacağım)</option>
                <option value="seller">Satıcıyım (Mağazam var)</option>
            </select>
            <p class="small text-muted mb-1">Güvenlik Sorusu: En sevdiğiniz renk nedir?</p>
            <input name="guvenlik" class="form-control mb-4" placeholder="Cevabınız" required>
            <button class="btn btn-main w-100 py-3">Kayıt Ol</button>
        </form>
    </div></div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
    return render_template_string(DESIGN + """
    <div class="container mt-5"><div class="card p-5 mx-auto shadow-lg" style="max-width:400px;">
        <h2 class="fw-bold text-center mb-4">Giriş Yap</h2>
        <form method="POST">
            <input name="username" class="form-control mb-3" placeholder="Kullanıcı Adı" required>
            <input name="password" type="password" class="form-control mb-3" placeholder="Şifre" required>
            <button class="btn btn-dark w-100 py-2">Giriş</button>
            <div class="text-center mt-3"><a href="/forgot" class="small text-muted">Şifremi Unuttum</a></div>
        </form>
    </div></div>
    """)

@app.route('/seller-panel')
@login_required
def seller_panel():
    if current_user.role != 'seller': return "Yetkiniz yok."
    urunler = Urun.query.filter_by(satici_id=current_user.id).all()
    satirlar = ""
    for u in urunler:
        satirlar += f"<tr><td>{u.ad}</td><td>{u.fiyat} TL</td><td>{u.kategori}</td><td><a href='/delete/{u.id}' class='text-danger'>Sil</a></td></tr>"
    
    return render_template_string(DESIGN + get_nav() + f"""
    <div class="container mt-4">
        <div class="card p-4 shadow-sm mb-4">
            <h3>Ürün Ekle (Mağaza Paneli)</h3>
            <form action="/add" method="POST" class="row g-3">
                <div class="col-md-4"><input name="ad" class="form-control" placeholder="Ürün Adı" required></div>
                <div class="col-md-2"><input name="fiyat" type="number" step="0.01" class="form-control" placeholder="Fiyat" required></div>
                <div class="col-md-3">
                    <select name="kategori" class="form-select">
                        <option value="Elektronik">Elektronik</option>
                        <option value="Giyim">Giyim</option>
                        <option value="Ev-Yasam">Ev & Yaşam</option>
                    </select>
                </div>
                <div class="col-md-3"><input name="gorsel" class="form-control" placeholder="Resim Linki"></div>
                <button class="btn btn-success">Ürünü Satışa Çıkar</button>
            </form>
        </div>
        <div class="card p-4 shadow-sm">
            <h4>Aktif Ürünleriniz</h4>
            <table class="table">{satirlar}</table>
        </div>
    </div>
    """)

@app.route('/add', methods=['POST'])
@login_required
def add():
    yeni = Urun(ad=request.form['ad'], fiyat=float(request.form['fiyat']), kategori=request.form['kategori'], gorsel=request.form.get('gorsel'), satici_id=current_user.id)
    db.session.add(yeni)
    db.session.commit()
    return redirect(url_for('seller_panel'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        db.session.execute(db.text('DROP TABLE IF EXISTS urun')) # Veritabanı yapısını güncellemek için
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
