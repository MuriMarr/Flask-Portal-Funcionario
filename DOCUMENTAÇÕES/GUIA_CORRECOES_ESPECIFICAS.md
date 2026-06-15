# 🔧 GUIA DE CORREÇÕES - Portal do Funcionário

## 1️⃣ CORRIGIR: config.py - Credenciais Hardcoded

### ❌ ANTES:
```python
from datetime import timedelta
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:13954@localhost:5432/portal_funcionario')
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

### ✅ DEPOIS:
```python
from datetime import timedelta
import os

class Config:
    # Credenciais OBRIGATORIAMENTE do ambiente
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Validação em tempo de início
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY não configurada no ambiente")
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError("DATABASE_URL não configurada no ambiente")
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # Sem acesso JavaScript
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
```

---

## 2️⃣ CORRIGIR: app.py - Debug Mode e Chave Secreta

### ❌ ANTES:
```python
import os
from datetime import datetime
from flask_login import current_user
from flask import Flask, redirect, url_for, session
from config import Config
from extensions import db, migrate, login_manager
from models import User
from dotenv import load_dotenv
from utils import format_timedelta

load_dotenv()
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN', 'admin@1234')

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.jinja_env.filters['format_timedelta'] = format_timedelta

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # ... resto do código ...

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
```

### ✅ DEPOIS:
```python
import os
import logging
from datetime import datetime
from flask_login import current_user
from flask import Flask, redirect, url_for, session
from config import Config
from extensions import db, migrate, login_manager
from models import User
from dotenv import load_dotenv
from utils import format_timedelta

load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.jinja_env.filters['format_timedelta'] = format_timedelta

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Criar pasta de uploads
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    @app.before_request
    def refresh_permanent_session():
        if current_user and current_user.is_authenticated:
            session.permanent = True
            session.modified = True

    # ... resto do código ...
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug_mode, host='127.0.0.1')
```

---

## 3️⃣ CORRIGIR: utils.py - admin_required Decorator

### ❌ ANTES:
```python
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper
```

### ✅ DEPOIS:
```python
from functools import wraps

def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    return wrapper
```

---

## 4️⃣ CORRIGIR: utils.py - log_action Function

### ❌ ANTES:
```python
# Chamada: log_action(usuario, acao)
def log_action(usuario, acao):
    novo_log = Log(usuario_id=usuario.id, acao=acao)  # Assume User object
    db.session.add(novo_log)
    db.session.commit()
```

### ✅ DEPOIS:
```python
def log_action(user_id, acao):
    """
    Registra uma ação no log do sistema
    
    Args:
        user_id: ID do usuário (int)
        acao: Descrição da ação (str)
    """
    try:
        novo_log = Log(user_id=user_id, acao=acao)
        db.session.add(novo_log)
        db.session.commit()
    except Exception as e:
        logger.error(f"Erro ao registrar log: {e}")
        db.session.rollback()
```

---

## 5️⃣ CORRIGIR: utils.py - calcular_saldo_ferias

### ❌ ANTES:
```python
def calcular_saldo_ferias(funcionario, hoje=None):
    hoje = hoje or date.today()
    admissao = funcionario.data_admissao

    meses = (hoje.year - admissao.year) * 12 + (hoje.month - admissao.month)
    dias_direito = (meses // 12) * 30 + (meses % 12) * 2.5
    dias_gozados = sum(f.ferias_dias for f in funcionario.ferias if f.status == "concedida")  # ❌ ERRO

    return round(dias_direito - dias_gozados, 1)
```

### ✅ DEPOIS:
```python
def calcular_saldo_ferias(funcionario, hoje=None):
    """
    Calcula saldo de férias do funcionário
    
    Regra: 30 dias a cada 12 meses
    """
    hoje = hoje or date.today()
    admissao = funcionario.data_admissao
    
    if not admissao:
        return 0

    meses = (hoje.year - admissao.year) * 12 + (hoje.month - admissao.month)
    dias_direito = (meses // 12) * 30 + (meses % 12) * 2.5
    
    # Campo correto é 'dias' não 'ferias_dias'
    dias_gozados = sum(
        f.dias for f in funcionario.ferias 
        if f.status == "aprovado"  # Status correto é 'aprovado'
    )

    return round(dias_direito - dias_gozados, 1)
```

---

## 6️⃣ CORRIGIR: auth/routes.py - Erro de Sintaxe

### ❌ ANTES:
```python
if not nome or not email or not senha:
    flash('Preencha todos os campos obrigatórios!' 'warning')  # ❌ FALTA VÍRGULA
    return redirect(url_for('funcionarios.registrar_funcionario'))
```

### ✅ DEPOIS:
```python
if not nome or not email or not senha:
    flash('Preencha todos os campos obrigatórios!', 'warning')  # ✅ VÍRGULA ADICIONADA
    return redirect(url_for('auth.registrar_funcionario'))
```

---

## 7️⃣ CORRIGIR: auth/routes.py - Validação de Tipo

### ❌ ANTES:
```python
@auth_bp.route('/registrar_funcionario', methods=['GET', 'POST'])
def registrar_funcionario():
    if request.method == 'POST':
        # ... coleta dados ...
        tipo = request.form.get('tipo', 'funcionario')  # ❌ Aceita do formulário!
        
        novo_user = User(
            nome=nome, email=email, senha=generate_password_hash(senha),
            tipo=tipo,  # ❌ Pode ser 'admin' ou 'superadmin'
            # ... resto ...
        )
```

### ✅ DEPOIS:
```python
@auth_bp.route('/registrar_funcionario', methods=['GET', 'POST'])
def registrar_funcionario():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        
        # Validar email
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Email inválido', 'danger')
            return redirect(url_for('auth.registrar_funcionario'))
        
        if not nome or not email or not senha:
            flash('Preencha todos os campos obrigatórios!', 'warning')
            return redirect(url_for('auth.registrar_funcionario'))
        
        # ✅ Tipo SEMPRE funcionário (nunca do formulário)
        tipo = 'funcionario'
        
        novo_user = User(
            nome=nome, email=email, tipo=tipo,
            # ... resto ...
        )
```

---

## 8️⃣ CORRIGIR: admin/dashboard.py - JOIN Correto

### ❌ ANTES:
```python
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    funcionarios = User.query.filter_by(empresa_id=current_user.empresa_id, tipo="funcionario").all()
    total_funcionarios = len(funcionarios)

    registros = Ponto.query.join(User).filter(User.empresa_id == current_user.empresa_id).all()  # ❌ JOIN ambíguo
    # ... resto ...
```

### ✅ DEPOIS:
```python
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Verificar autorização
    if current_user.tipo != 'admin' or current_user.empresa_id is None:
        abort(403)
    
    funcionarios = User.query.filter_by(
        empresa_id=current_user.empresa_id, 
        tipo="funcionario"
    ).all()
    total_funcionarios = len(funcionarios)

    # ✅ JOIN explícito
    registros = Ponto.query.join(
        User, Ponto.user_id == User.id
    ).filter(User.empresa_id == current_user.empresa_id).all()
    
    total_registros = len(registros)
    # ... resto ...
```

---

## 9️⃣ CORRIGIR: documentos/documentos.py - Imports

### ❌ ANTES:
```python
from routes import admin_bp, funcionarios_bp  # ❌ IMPORT ERRADO
from routes.common.pdf_utils import gerar_pdf
```

### ✅ DEPOIS:
```python
from routes.admin import admin_bp
from routes.funcionarios import funcionarios_bp
from routes.common.pdf_utils import gerar_pdf
```

---

## 🔟 CORRIGIR: requirements.txt - Pacotes Faltantes

### ❌ ANTES:
```
Flask==3.1.3
Flask-Login==0.6.3
# ... sem Flask-WeasyPrint ...
```

### ✅ DEPOIS:
```
Flask==3.1.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
Flask-Migrate==4.1.0
Flask-WeasyPrint==1.1.0
weasyprint==62.3
Flask-WTF==1.2.1
psycopg2-binary==2.9.11
python-dotenv==1.2.2
Werkzeug==3.1.8
```

---

## 1️⃣1️⃣ CORRIGIR: admin/ferias.py - Múltiplos Erros

### ❌ ANTES:
```python
@admin_bp.route("/ferias/<int:usuario_id>")
@login_required
@admin_required
def ferias_funcionario(usuario_id):
    funcionario = User.query.get_or_404(usuario_id)
    ferias_list = Ferias.query.filter_by(usuario_id=usuario_id).order_by(Ferias.inicio.desc()).all()
    dias_trabalhados = (datetime.now().date() - funcionario.date_admissao).days  # ❌ date_admissao
    saldo = max(0, (dias_trabalhados // 365) * 30 - sum(f.dias for f in ferias_list))
    return render_template("admin/ferias_admin.html", funcionario=funcionario, ferias_list=ferias_list, saldo=saldo)

@admin_bp.route("ferias/<int:usuario_id>/editar/<int:ferias_id>", methods=["GET", "POST"])  # ❌ Falta /
@login_required
@admin_required
def editar_ferias(usuario_id, ferias_id):
    funcionario = User.query.get_or_404(usuario_id)
    ferias = Ferias.query.get_or_404(ferias_id)

    if request.method == "POST":
        ferias.inicio = request.form.get("inicio")  # ❌ String, não Date
        ferias.fim = request.form.get("fim")  # ❌ String
        ferias.data_fim = request.form.get("fim")  # ❌ Campo não existe
        ferias.dias = request.form.get("dias")  # ❌ String, não int
        # ...
```

### ✅ DEPOIS:
```python
@admin_bp.route("/ferias/<int:usuario_id>")
@login_required
@admin_required
def ferias_funcionario(usuario_id):
    funcionario = User.query.get_or_404(usuario_id)
    
    # Verificar autorização
    if funcionario.empresa_id != current_user.empresa_id:
        abort(403)
    
    ferias_list = Ferias.query.filter_by(
        funcionario_id=usuario_id
    ).order_by(Ferias.inicio.desc()).all()
    
    dias_trabalhados = (datetime.now().date() - funcionario.data_admissao).days  # ✅ Correto
    saldo = max(0, (dias_trabalhados // 365) * 30 - sum(f.dias for f in ferias_list))
    
    return render_template(
        "admin/ferias_admin.html",
        funcionario=funcionario,
        ferias_list=ferias_list,
        saldo=saldo
    )

@admin_bp.route("/ferias/<int:usuario_id>/editar/<int:ferias_id>", methods=["GET", "POST"])  # ✅ / adicionado
@login_required
@admin_required
def editar_ferias(usuario_id, ferias_id):
    funcionario = User.query.get_or_404(usuario_id)
    ferias = Ferias.query.get_or_404(ferias_id)
    
    # Autorização
    if ferias.funcionario_id != usuario_id or funcionario.empresa_id != current_user.empresa_id:
        abort(403)

    if request.method == "POST":
        try:
            # ✅ Converter strings para tipos corretos
            inicio = datetime.strptime(request.form.get("inicio"), "%Y-%m-%d").date()
            fim = datetime.strptime(request.form.get("fim"), "%Y-%m-%d").date()
            dias = int(request.form.get("dias", 0))
            
            ferias.inicio = inicio
            ferias.fim = fim
            ferias.dias = dias
            ferias.adiantamento_decimo = bool(request.form.get("adiantamento_decimo"))
            ferias.aprovado = bool(request.form.get("aprovado"))

            db.session.commit()
            flash("Férias atualizadas com sucesso!", "success")
        except ValueError:
            flash("Dados inválidos", "danger")
            
        return redirect(url_for("admin.ferias_funcionario", usuario_id=usuario_id))
    
    return render_template("admin/editar_ferias.html", funcionario=funcionario, ferias=ferias)
```

---

## 1️⃣2️⃣ CRIAR: Função calcular_horas_ponto (FALTANDO)

### 📍 Adicionar em: utils.py

```python
def calcular_horas_ponto(ponto, carga=None):
    """
    Calcula horas de um ponto de entrada/saída
    
    Args:
        ponto: Objeto Ponto
        carga: Timedelta da jornada padrão (padrão: 8 horas)
    
    Returns:
        dict: {
            'total_trabalhado': timedelta,
            'saldo': timedelta,
            'extras': timedelta,
            'deficit': timedelta
        }
    """
    if carga is None:
        carga = timedelta(hours=8)
    
    marcacoes = Marcacao.query.filter_by(ponto_id=ponto.id).order_by(Marcacao.hora).all()
    
    if len(marcacoes) < 2:
        return {
            'total_trabalhado': timedelta(),
            'saldo': timedelta(),
            'extras': timedelta(),
            'deficit': carga
        }
    
    # Calcular tempo trabalhado considerando intervalo de almoço
    entrada = datetime.combine(ponto.data, marcacoes[0].hora)
    saida = datetime.combine(ponto.data, marcacoes[-1].hora)
    
    # Se houver 3+ marcações, considera intervalo
    if len(marcacoes) >= 3:
        saida_almoco = datetime.combine(ponto.data, marcacoes[1].hora)
        retorno_almoco = datetime.combine(ponto.data, marcacoes[2].hora)
        intervalo = retorno_almoco - saida_almoco
    else:
        intervalo = timedelta()
    
    total_trabalhado = saida - entrada - intervalo
    
    if total_trabalhado > carga:
        extras = total_trabalhado - carga
        saldo = timedelta()
    else:
        extras = timedelta()
        saldo = total_trabalhado - carga
    
    deficit = max(timedelta(), -saldo)
    
    return {
        'total_trabalhado': total_trabalhado,
        'saldo': saldo,
        'extras': extras,
        'deficit': deficit
    }
```

---

## 1️⃣3️⃣ CORRIGIR: extensions.py - Login Manager

### ❌ ANTES:
```python
from flask_login import LoginManager

db= SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
```

### ✅ DEPOIS:
```python
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor, faça login para acessar esta página.'
login_manager.login_message_category = 'info'
```

---

## 1️⃣4️⃣ CRIAR: .env.example

```
# Criar arquivo .env com variáveis de ambiente

FLASK_ENV=development
SECRET_KEY=seu_segredo_super_secreto_aqui_mude_em_producao
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/portal_funcionario
CHAVE_SECRETA_ADMIN=sua_chave_admin_segura_aqui
```

---

## 📋 Checklist de Implementação

- [ ] Corrigir credenciais em config.py
- [ ] Remover debug=True de app.py
- [ ] Adicionar @wraps a decorators
- [ ] Corrigir log_action
- [ ] Corrigir calcular_saldo_ferias
- [ ] Corrigir erro de sintaxe em auth/routes.py
- [ ] Validar tipo de usuário em auth/routes.py
- [ ] Corrigir JOINs em admin/dashboard.py
- [ ] Corrigir imports em documentos.py
- [ ] Adicionar pacotes em requirements.txt
- [ ] Corrigir ferias.py
- [ ] Implementar calcular_horas_ponto
- [ ] Adicionar arquivo .env.example
- [ ] Rodar testes
- [ ] Testar em staging
