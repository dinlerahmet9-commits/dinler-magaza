import os
from flask import Flask, render_template_string, request, redirect, session

app = Flask(__name__)
app.secret_key = "dinler_anahtar_99"

# TASARIM FONKSİYONU
def sayfa_yap(icerik):
    return f"""
    <html>
    <head><link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet"></head>
    <body class="p-5 bg-light text-center">
        <nav class="mb-4"><a href="/" class="me-3">Ana Sayfa</a> <a href="/admin">Admin</a></nav>
        <div class="card p-4 shadow-sm" style="max-width:600px; margin:auto;">{icerik}</div>
    </body>
    </html>
    """

@app.route('/')
def index():
    return sayfa_yap("<h1>🛒 Dinler Satış</h1><p>Sistem Hazır! Ürün eklemek için Admin paneline gidin.</p>")

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        if request.form.get('sifre') == "dinler16":
            session['admin'] = True
            return redirect('/admin')
    
    if not session.get('admin'):
        return sayfa_yap('<form method="POST">Şifre: <input type="password" name="sifre"><button type="submit">Giriş</button></form>')
    
    return sayfa_yap("<h2>Yönetici Paneli</h2><p>Giriş Başarılı!</p>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
