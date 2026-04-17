import os
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dinler_mega_premium_secret_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dinler_final.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# --- VERİ MODELLERİ ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='buyer') # 'buyer' veya 'seller'
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

# --- ULTRA MODERN TASARIM (CSS) ---
DESIGN = """
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
<style>
    :root { --main: #ff6000; --dark: #121212; --bg: #f8f9fa; }
    body { background: var(--bg); font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    .navbar { background: white; border-bottom: 3px solid var(--main); box-shadow: 0 2px 15px rgba(0,0,0,0.05); }
    .navbar-brand { font-weight: 800; color: var(--main) !important; font-size: 1.6rem; }
    .btn-orange { background: var(--main); color: white; border-radius: 10px; font-weight: 600; border: none; transition: 0.3s; }
    .btn-orange:hover { background: #e65600; color: white; transform: scale(1.05); }
    .product-card { border: none; border-radius: 20px; background: white; transition: 0.4s; height: 100%; border: 1px solid #eee; }
    .product-card:hover { transform: translateY(-10px); box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
    .category-link { text-decoration: none; color: #555; display: block; padding: 10px; border-radius: 10px; transition: 0.2s; }
    .category-link:hover { background: #fff1e6; color: var(--main); padding-left: 15px; }
    .admin-box { background: white; border-radius: 25px; padding: 40px; box-shadow: 0 10px 40px rgba(0,0,0,0.05); }
</style>
"""

def get_nav():
    auth_links = ""
    if current_user.is_authenticated:
        panel = url_for('seller_panel') if current_user.role == 'seller' else "#"
        auth_links = f'''
            <li class="nav-item"><a class="nav-link fw-bold text-dark" href="{panel}">Panelim</a></li>
            <li class="nav-item"><a class="nav-link text-danger ms-3" href="/logout"><i class="fa fa-sign-out"></i></a></li>
        '''
    else:
        auth_links = '''
            <li class="nav-item"><a class="nav-link text-dark" href="/login">Giriş</a></li>
            <li class="nav-item"><a class="btn btn-orange btn-sm px-4 ms-2" href="/register">Kayıt Ol</a></li>
        '''
    return f'''
    <nav class="navbar navbar-expand-lg sticky-top p-3">
        <div class="container">
            <a class="navbar-brand" href="/">DİNLER <span style="color:#222">SATIŞ</span></a>
            <div class="ms-auto"><ul class="navbar-nav align-items-center">{auth_links}</ul></div>
        </div>
    </nav>
    '''

# --- YOLLAR ---
@app.route('/')
def index():
    urunler = Urun.query.all()
    kartlar = ""
    for u in urunler:
        img = u.gorsel if u.gorsel else "https://via.placeholder.com/400x400.png?text=Dinler+Satis"
        kartlar += f'''
        <div class="col-lg-4 col-md-6 mb-4">
            <div class="product-card p-3 shadow-sm">
                <img src="{img}" class="rounded-4 mb-3 w-100" style="height:250px; object-fit:cover;">
                <span class="badge bg-light text-muted mb-2 px-3 py-2">{u.kategori}</span>
                <h5 class="fw-bold mb-1">{u.ad}</h5>
                <div class="d-flex justify-content-between align-items-center mt-3">
                    <span class="fs-4 fw-bold text-dark">{u.fiyat} TL</span>
                    <button class="btn btn-orange px-4">Sepete</button>
                </div>
            </div>
        </div>
        '''
    return render_template_string(DESIGN + get_nav() + f"""
    <div class="container mt-5">
        <div class="row">
            <div class="col-md-3 mb-4">
                <div class="card border-0 p-4 rounded-4 shadow-sm">
                    <h5 class="fw-bold mb-4">Kategoriler</h5>
                    <a href="/" class="category-link fw-bold">Tüm Ürünler</a>
                    <a href="#" class="category-link">Elektronik</a>
                    <a href="#" class="category-link">Giyim & Moda</a>
                    <a href="#" class="category-link">Ev & Yaşam</a>
                </div>
            </div>
            <div class="col-md-9">
                <div class="row">{kartlar if urunler else '<div class="text-center py-5"><h4>Vitrin henüz boş, bir satıcı girişi yapıp ürün ekleyebilirsin!</h4></div>'}</div>
            </div>
        </div>
    </div>
    """)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        hashed_pw = generate_password_hash(request.form['password'])
        new_user = User(username=request.form['username'], password=hashed_pw, role=request.form['role'], guvenlik_cevabi=request.form['guvenlik'].lower())
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template_string(DESIGN + """
    <div class="container mt-5 pt-5 text-center">
        <div class="admin-box mx-auto shadow-lg" style="max-width:450px;">
            <h3 class="fw-bold mb-4">Ücretsiz Hesap Aç</h3>
            <form method="POST">
                <input name="username" class="form-control form-control-lg mb-3 rounded-4" placeholder="Kullanıcı Adı" required>
                <input name="password" type="password" class="form-control form-control-lg mb-3 rounded-4" placeholder="Şifre" required>
                <select name="role" class="form-select form-select-lg mb-3 rounded-4">
                    <option value="seller">Satıcıyım (Mağaza)</option>
                    <option value="buyer">Alıcıyım (Müşteri)</option>
                </select>
                <input name="guvenlik" class="form-control mb-4 rounded-4" placeholder="Güvenlik: En sevdiğin renk?" required>
                <button type="submit" class="btn btn-orange w-100 py-3 rounded-4 fs-5 shadow">Hesabı Oluştur</button>
            </form>
        </div>
    </div>
    """)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for('index'))
    return render_template_string(DESIGN + """
    <div class="container mt-5 pt-5 text-center">
        <div class="admin-box mx-auto shadow-lg" style="max-width:400px;">
            <h3 class="fw-bold mb-4">Tekrar Hoş Geldin</h3>
            <form method="POST">
                <input name="username" class="form-control form-control-lg mb-3 rounded-4 text-center" placeholder="Kullanıcı Adı" required>
                <input name="password" type="password" class="form-control form-control-lg mb-4 rounded-4 text-center" placeholder="Şifre" required>
                <button type="submit" class="btn btn-dark w-100 py-3 rounded-4 fs-5 mb-3">Giriş Yap</button>
                <a href="/register" class="text-decoration-none text-muted">Henüz hesabın yok mu? Kayıt ol.</a>
            </form>
        </div>
    </div>
    """)

@app.route('/seller-panel')
@login_required
def seller_panel():
    if current_user.role != 'seller': return redirect('/')
    urunler = Urun.query.filter_by(satici_id=current_user.id).all()
    satirlar = ""
    for u in urunler:
        satirlar += f"<tr><td>{u.ad}</td><td>{u.fiyat} TL</td><td><a href='/delete/{u.id}' class='btn btn-sm btn-danger rounded-pill px-3'>Sil</a></td></tr>"
    return render_template_string(DESIGN + get_nav() + f"""
    <div class="container mt-5">
        <div class="admin-box mb-4">
            <h3 class="fw-bold mb-4">Hızlı Ürün Ekle</h3>
            <form action="/add" method="POST" class="row g-3">
                <div class="col-md-5"><input name="ad" class="form-control" placeholder="Ürün İsmi" required></div>
                <div class="col-md-2"><input name="fiyat" type="number" step="0.01" class="form-control" placeholder="Fiyat" required></div>
                <div class="col-md-3"><select name="kategori" class="form-select"><option>Elektronik</option><option>Moda</option><option>Diger</option></select></div>
                <div class="col-md-2"><button class="btn btn-orange w-100">Ekle</button></div>
                <div class="col-12"><input name="gorsel" class="form-control" placeholder="Görsel URL (İsteğe bağlı)"></div>
            </form>
        </div>
        <div class="admin-box">
            <h4 class="fw-bold mb-3">Mağaza Envanterin</h4>
            <table class="table table-hover mt-3"><thead><tr><th>Ürün</th><th>Fiyat</th><th>İşlem</th></tr></thead><tbody>{satirlar}</tbody></table>
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

@app.route('/delete/<int:id>')
@login_required
def delete(id):
    u = Urun.query.get(id)
    if u.satici_id == current_user.id:
        db.session.delete(u)
        db.session.commit()
    return redirect(url_for('seller_panel'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    with app.app_context():
        # DİKKAT: Veritabanını her güncellemede temizlemek ve hataları ayıklamak için aşağıdaki satır kritik.
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
