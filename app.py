from flask import Flask, request, render_template, redirect, url_for, session, flash
from flask_dance.contrib.google import make_google_blueprint, google
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from functools import wraps
import logging

# Configuração inicial
load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY") or os.urandom(24)

# Configurações de sessão
app.config.update(
    SESSION_COOKIE_SECURE=False,  # True em produção com HTTPS
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configurações para desenvolvimento
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Configuração da API OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "http://localhost:5000")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "SwiftAI Local")

AIS = {
    "DeepSeek-R1": "deepseek/deepseek-r1:free",
    "DeepSeek Chat": "deepseek/deepseek-chat:free", 
    "Google Gemma": "google/gemma-3-1b-it:free",
}

# Modelos do banco de dados
class User(db.Model):
    id = db.Column(db.String(120), primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(120), unique=True)
    avatar = db.Column(db.String(200))
    chats = db.relationship('Chat', backref='user', lazy=True)

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(120), db.ForeignKey('user.id'))
    question = db.Column(db.Text)
    answer = db.Column(db.Text)
    image_url = db.Column(db.String(200))
    ai_model = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Decorator para rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("Por favor, faça login para acessar esta página", "warning")
            return redirect(url_for("login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Configuração do OAuth Google com escopos atualizados
google_bp = make_google_blueprint(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    scope=[
        "openid",
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ],
    redirect_to="google_callback",
    reprompt_consent=True,
    offline=True
)
app.register_blueprint(google_bp, url_prefix="/login")

# Filtro para formatar datas
@app.template_filter('datetimeformat')
def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if isinstance(value, str):
        value = datetime.fromisoformat(value)
    return value.strftime(format)

# Rotas de autenticação
@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("chat"))
    return render_template("login.html")

@app.route("/login/google/authorized")
def google_callback():
    if not google.authorized:
        flash("Falha na autorização com Google", "error")
        return redirect(url_for("login"))
    
    try:
        resp = google.get("/oauth2/v2/userinfo")
        if not resp.ok:
            flash("Falha ao obter dados do usuário", "error")
            return redirect(url_for("login"))
        
        user_info = resp.json()
        user = User.query.get(user_info["id"])
        
        if not user:
            user = User(
                id=user_info["id"],
                name=user_info["name"],
                email=user_info["email"],
                avatar=user_info.get("picture", "/static/user-default.png")
            )
            db.session.add(user)
            db.session.commit()
        
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_avatar"] = user.avatar
        
        return redirect(url_for("chat"))
    
    except Exception as e:
        flash(f"Erro durante o login: {str(e)}", "error")
        return redirect(url_for("login"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Rotas da aplicação
@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("chat"))
    return render_template("home.html")

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    user = User.query.get(session["user_id"])
    
    if request.method == "POST":
        user_input = request.form.get("question")
        image_url = request.form.get("image_url")
        selected_ai = request.form.get("ai")

        if not user_input and not image_url:
            flash("Por favor, insira uma pergunta ou uma imagem", "error")
            return redirect(url_for("chat"))

        if selected_ai not in AIS:
            flash("Modelo AI não encontrado", "error")
            return redirect(url_for("chat"))

        model = AIS[selected_ai]
        messages = [{"role": "user", "content": []}]

        if user_input:
            messages[0]["content"].append({"type": "text", "text": user_input})

        if image_url:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {"url": image_url}
            })

        try:
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": YOUR_SITE_URL,
                    "X-Title": YOUR_SITE_NAME,
                },
                json={
                    "model": model,
                    "messages": messages,
                },
                timeout=30
            )

            if response.status_code == 200:
                answer = response.json()["choices"][0]["message"]["content"]
            else:
                error_msg = response.json().get("error", {}).get("message", "Erro desconhecido")
                raise Exception(f"API Error: {error_msg}")

        except requests.exceptions.Timeout:
            flash("Tempo de resposta excedido. Tente novamente.", "error")
            return redirect(url_for("chat"))
        except Exception as e:
            flash(f"Erro ao processar sua solicitação: {str(e)}", "error")
            return redirect(url_for("chat"))

        new_chat = Chat(
            user_id=user.id,
            question=user_input,
            answer=answer,
            image_url=image_url,
            ai_model=selected_ai
        )
        db.session.add(new_chat)
        db.session.commit()
        flash("Resposta recebida com sucesso!", "success")

    chat_history = Chat.query.filter_by(user_id=user.id).order_by(Chat.timestamp.desc()).all()
    return render_template("chat.html", 
                         chat_history=chat_history,
                         ais=AIS.keys(),
                         user=user)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)