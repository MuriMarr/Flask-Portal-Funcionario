# 🔧 GUIA DE CORREÇÕES ESPECÍFICAS

## Como Usar Este Documento
Para cada problema crítico, este documento mostra:
1. ❌ Código atual (incorreto)
2. ✅ Código corrigido
3. 📝 Explicação
4. 📂 Arquivo afetado

---

## CORREÇÃO #1: Remover Credenciais Hardcoded

### Arquivo: `config.py`

#### ❌ ANTES:
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

#### ✅ DEPOIS:
```python
from datetime import timedelta
import os

class Config:
    # Validar que as chaves obrigatórias estão definidas
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DATABASE_URL = os.environ.get('DATABASE_URL')
    
    if not SECRET_KEY or not DATABASE_URL:
        raise ValueError(
            "Variáveis obrigatórias não configuradas: SECRET_KEY, DATABASE_URL. "
            "Configure no arquivo .env"
        )
    
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static/uploads')

    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(hours=8)
    
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

#### 📝 Explicação:
- Remove padrões hardcoded que são vulneráveis
- Força que `SECRET_KEY` e `DATABASE_URL` sejam definidos em `.env`
- Levanta erro claro se estiverem faltando

---

## CORREÇÃO #2: Remover Chave Admin Hardcoded

### Arquivo: `app.py`

#### ❌ ANTES:
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
```

#### ✅ DEPOIS:
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
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN')

if not CHAVE_SECRETA_ADMIN:
    raise ValueError(
        "CHAVE_SECRETA_ADMIN não configurada. Configure no arquivo .env"
    )
```

#### 📝 Explicação:
- Remove padrão inseguro
- Força configuração em `.env`

---

## CORREÇÃO #3: Corrigir Função `calcular_horas_ponto()`

### Arquivo: `utils.py`

#### ❌ ANTES:
```python
# ... função não existe, causando erro em relatorios e admin
```

#### ✅ DEPOIS:
Adicionar esta função em `utils.py` (próximo à função `to_time`):

```python
def calcular_horas_ponto(ponto, carga=None):
    """
    Calcula horas trabalhadas, extras e deficits para um ponto (dia).
    
    Args:
        ponto: Objeto Ponto com marcações do dia
        carga: Timedelta com carga horária esperada (padrão: 8 horas)
    
    Returns:
        dict com:
            - total_trabalhado: horas efetivamente trabalhadas
            - extras: horas acima da carga
            - deficit: horas faltantes
    """
    from models import Marcacao
    
    if carga is None:
        carga = timedelta(hours=8)
    
    # Buscar marcações do dia
    marcacoes = Marcacao.query.filter_by(ponto_id=ponto.id)\
        .order_by(Marcacao.hora).all()
    
    # Se menos de 2 marcações, não há jornada completa
    if len(marcacoes) < 2:
        return {
            "total_trabalhado": timedelta(),
            "extras": timedelta(),
            "deficit": carga
        }
    
    # Converter para datetime
    entrada = to_time(ponto.data, marcacoes[0].hora)
    saida = to_time(ponto.data, marcacoes[-1].hora)
    
    # Calcular pausa de almoço (se houver mais de 2 marcações)
    pausa_almoco = timedelta()
    if len(marcacoes) > 2:
        saida_almoco = to_time(ponto.data, marcacoes[1].hora)
        retorno_almoco = to_time(ponto.data, marcacoes[2].hora)
        pausa_almoco = retorno_almoco - saida_almoco
    
    # Calcular total trabalhado
    total_trabalhado = saida - entrada - pausa_almoco
    
    # Validar se total é positivo
    if total_trabalhado.total_seconds() < 0:
        total_trabalhado = timedelta()
    
    # Calcular extras ou deficit
    if total_trabalhado > carga:
        extras = total_trabalhado - carga
        deficit = timedelta()
    else:
        extras = timedelta()
        deficit = carga - total_trabalhado
    
    return {
        "total_trabalhado": total_trabalhado,
        "extras": extras,
        "deficit": deficit
    }
```

#### 📝 Explicação:
- Função estava sendo chamada mas não implementada
- Calcula horas considerando pausa de almoço
- Retorna dict com total, extras e deficit

---

## CORREÇÃO #4: Corrigir Campo `data_admissao`

### Arquivo: `models.py`

#### ❌ ANTES:
```python
class User(UserMixin, db.Model):
    # ...
    data_admissao = db.Column(db.Date, default=date.today)  # ❌ Faltam parênteses!
    data_demissao = db.Column(db.Date, nullable=True)
```

#### ✅ DEPOIS:
```python
class User(UserMixin, db.Model):
    # ...
    data_admissao = db.Column(db.Date, default=lambda: date.today())  # ✅ Com parênteses/lambda
    data_demissao = db.Column(db.Date, nullable=True)
```

#### 📝 Explicação:
- `date.today` sem parênteses passa a função, não a data
- `lambda: date.today()` chama a função a cada novo usuário

---

## CORREÇÃO #5: Corrigir Log Model e uso

### Arquivo: `models.py` e `utils.py`

#### ❌ ANTES - models.py:
```python
class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    acao = db.Column(db.String(255), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    # ✅ Campo está correto aqui
```

#### ❌ ANTES - utils.py:
```python
def log_action(usuario, acao):
    novo_log = Log(usuario_id=usuario.id, acao=acao)  # ❌ usuario_id não existe!
    db.session.add(novo_log)
    db.session.commit()
```

#### ✅ DEPOIS - utils.py:
```python
def log_action(usuario, acao):
    novo_log = Log(user_id=usuario.id, acao=acao)  # ✅ Usar user_id
    db.session.add(novo_log)
    db.session.commit()
```

#### 📝 Explicação:
- Campo no Model é `user_id`, não `usuario_id`
- Padronizar nomes em todo projeto

---

## CORREÇÃO #6: Corrigir Decorator `admin_required`

### Arquivo: `utils.py`

#### ❌ ANTES:
```python
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # ❌ Gambiarra
    return wrapper
```

#### ✅ DEPOIS:
```python
def admin_required(func):
    @wraps(func)  # ✅ Usar @wraps
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    return wrapper
```

#### 📝 Explicação:
- `@wraps` preserva metadados da função original
- Melhor que atribuição manual de `__name__`

---

## CORREÇÃO #7: Corrigir Relacionamentos em Empresa

### Arquivo: `models.py`

#### ❌ ANTES:
```python
class Empresa(db.Model):
    # ...
    admin = db.relationship("User", foreign_keys=[admin_id], backref="empresa_administradas")
    users = db.relationship("User", backref="empresa", lazy=True, foreign_keys=lambda: [User.empresa_id])
    # ❌ backref="empresa" pode conflitar com o outro relacionamento
```

#### ✅ DEPOIS:
```python
class Empresa(db.Model):
    # ...
    admin = db.relationship(
        "User", 
        foreign_keys=[admin_id], 
        backref="empresas_administradas"  # ✅ Nome único
    )
    users = db.relationship(
        "User", 
        backref="empresa_trabalho",  # ✅ Nome único
        lazy=True, 
        foreign_keys=lambda: [User.empresa_id]
    )
```

#### 📝 Explicação:
- Backrefs devem ter nomes únicos para evitar conflitos
- Allows `usuario.empresa_trabalho` e `usuario.empresas_administradas`

---

## CORREÇÃO #8: Corrigir Callback do Login Manager

### Arquivo: `app.py`

#### ❌ ANTES:
```python
@login_manager.user_loader
def carregar_usuario(user_id):
    return User.query.get(int(user_id))  # ❌ Sem tratamento de erro
```

#### ✅ DEPOIS:
```python
@login_manager.user_loader
def carregar_usuario(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None  # Retorna None se conversão falhar
```

#### 📝 Explicação:
- Trata erro se `user_id` não for número
- Evita erro 500

---

## CORREÇÃO #9: Adicionar Tratamento de Exceção Global

### Arquivo: `app.py`

#### ❌ ANTES:
```python
def create_app():
    app = Flask(__name__)
    # ... resto do código
    return app
```

#### ✅ DEPOIS:
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # ... inicializações (db, migrate, etc)
    
    # ✅ Handlers de erro
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        # Aqui você pode logar o erro
        return render_template('500.html'), 500
    
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(403)
    def forbidden_error(error):
        flash('Acesso negado', 'danger')
        return redirect(url_for('funcionarios.dashboard'))
    
    # ... resto do código
    
    return app
```

#### 📝 Explicação:
- Trata erros globalmente
- Evita exposição de stack trace
- Melhor UX com mensagens customizadas

---

## CORREÇÃO #10: Corrigir Session Permanente

### Arquivo: `app.py`

#### ❌ ANTES:
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # ...
    
    @app.before_request
    def refresh_permanent_session():
        if current_user and current_user.is_authenticated:
            session.permanent = True
            session.modified = True
```

#### ✅ DEPOIS:
```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # Remover SESSION_PERMANENT daqui, já está em Config
    
    # ...
    
    @app.before_request
    def refresh_permanent_session():
        try:
            if current_user and current_user.is_authenticated:
                session.permanent = True
                session.modified = True
        except Exception:
            # Se houver erro com session, apenas prosseguir
            pass
```

#### 📝 Explicação:
- Evita duplicação com `config.py`
- Trata exceções de session

---

## CORREÇÃO #11: Adicionar Validação em Login

### Arquivo: `auth/routes.py`

#### ❌ ANTES:
```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        user = User.query.filter_by(email=email).first()

        if user and user.check_senha(senha):
            login_user(user, remember=False)
            flash("Login realizado com sucesso", "success")
            # ...
        else:
            flash("Usuário desconhecido. Contate o suporte.", "danger")

    return render_template("login.html")
```

#### ✅ DEPOIS:
```python
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        
        # ✅ Validação básica
        if not email or not senha:
            flash("Email e senha são obrigatórios", "danger")
            return render_template("login.html")
        
        # ✅ Validação de email
        if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash("Email inválido", "danger")
            return render_template("login.html")
        
        user = User.query.filter_by(email=email).first()

        if user and user.check_senha(senha):
            login_user(user, remember=False)
            flash("Login realizado com sucesso", "success")

            if user.tipo == "superadmin": 
                return redirect(url_for("superadmin.dashboard"))
            elif user.tipo == "admin":
                return redirect(url_for("admin.dashboard"))
            elif user.tipo == "funcionario":
                return redirect(url_for("funcionarios.dashboard"))
        else:
            # ❌ Mensagem genérica por segurança (não revela se email existe)
            flash("Email ou senha incorretos", "danger")

    return render_template("login.html")
```

#### 📝 Explicação:
- Valida campos obrigatórios
- Valida formato de email
- Não revela se email existe no BD (segurança)

---

## CORREÇÃO #12: Adicionar Filtro de Usuários Ativos

### Arquivo: `routes/admin/dashboard.py`

#### ❌ ANTES:
```python
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    funcionarios = User.query.filter_by(empresa_id=current_user.empresa_id, tipo="funcionario").all()
    # ❌ Inclui funcionários inativos/demitidos
    # ...
```

#### ✅ DEPOIS:
```python
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    funcionarios = User.query.filter_by(
        empresa_id=current_user.empresa_id, 
        tipo="funcionario",
        ativo=True  # ✅ Apenas ativos
    ).all()
    # ...
```

#### 📝 Explicação:
- Filtra apenas funcionários ativos
- Evita contar dados de demitidos

---

## Arquivo .env Necessário

Crie um arquivo `.env` na raiz do projeto:

```env
# Segurança
SECRET_KEY=sua-chave-secreta-muito-segura-aqui
CHAVE_SECRETA_ADMIN=sua-chave-admin-muito-segura-aqui

# Banco de Dados
DATABASE_URL=postgresql+psycopg2://seu_usuario:sua_senha@localhost:5432/portal_funcionario

# Flask
FLASK_ENV=production  # ou development
FLASK_DEBUG=0  # Mude para 1 apenas em desenvolvimento
```

---

## Arquivo .gitignore Necessário

Crie/atualize `.gitignore`:

```
.env
__pycache__/
*.pyc
*.pyo
.vscode/
.idea/
venv/
env/
static/uploads/*
!static/uploads/.gitkeep
*.db
.DS_Store
```

---

## Ordem de Implementação

1. ✅ Criar `.env` com valores seguros
2. ✅ Criar `.gitignore`
3. ✅ Corrigir `config.py` e `app.py`
4. ✅ Implementar `calcular_horas_ponto()` em `utils.py`
5. ✅ Corrigir `models.py` (data_admissao, relacionamentos, Log)
6. ✅ Corrigir decorators em `utils.py`
7. ✅ Adicionar tratamento de erros em `app.py`
8. ✅ Validação em `auth/routes.py`
9. ✅ Filtros em `admin/dashboard.py` e outros dashboards
10. ✅ Testar login e dashboard

