# 🚀 PLANO DE AÇÃO - PRÓXIMOS PASSOS

## 📋 Visão Geral

Você tem **53 erros** no seu aplicativo Portal do Funcionário. Este documento guia você através de um plano prático para corrigi-los.

---

## 🎯 Fase 1: Preparação (30 minutos)

### Passo 1.1: Criar Arquivo `.env`

```bash
# Na raiz do projeto, copie:
cp .env.example .env

# Edite .env e mude os valores:
SECRET_KEY=seu-valor-aleatorio-seguro
CHAVE_SECRETA_ADMIN=outra-chave-aleatoria
DATABASE_URL=postgresql+psycopg2://postgres:13954@localhost:5432/portal_funcionario
FLASK_ENV=development
FLASK_DEBUG=1
```

### Passo 1.2: Criar/Atualizar `.gitignore`

Crie um arquivo `.gitignore` na raiz:

```
.env
.env.local
__pycache__/
*.pyc
*.pyo
*.egg-info/
.vscode/
.idea/
venv/
env/
static/uploads/*
!static/uploads/.gitkeep
*.db
.DS_Store
*.log
```

### Passo 1.3: Verificar Estado Atual

```bash
# Tente rodar o app para ver os erros
python app.py

# Você pode ver:
# - ImportError: cannot import name 'calcular_horas_ponto'
# - AttributeError: 'Log' has no attribute 'usuario_id'
# Etc
```

---

## 🔴 Fase 2: Corrigir Críticos (2-3 horas)

### Tarefa 2.1: Corrigir `config.py`

**Arquivo:** `config.py`

```python
# ❌ REMOVA:
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:13954@localhost:5432/portal_funcionario')

# ✅ ADICIONE:
DATABASE_URL = os.environ.get('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError(
        "DATABASE_URL não configurada. Configure no arquivo .env"
    )

SQLALCHEMY_DATABASE_URI = DATABASE_URL

# ❌ REMOVA:
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')

# ✅ ADICIONE:
SECRET_KEY = os.environ.get('SECRET_KEY')

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY não configurada. Configure no arquivo .env"
    )
```

**Tempo:** 5 minutos

---

### Tarefa 2.2: Corrigir `app.py`

**Arquivo:** `app.py`

```python
# ❌ REMOVA:
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN', 'admin@1234')

# ✅ ADICIONE:
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN')

if not CHAVE_SECRETA_ADMIN:
    raise ValueError(
        "CHAVE_SECRETA_ADMIN não configurada. Configure no arquivo .env"
    )
```

E adicione isto na função `create_app()` após `app.config.from_object(Config)`:

```python
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def forbidden_error(error):
    flash('Acesso negado', 'danger')
    return redirect(url_for('funcionarios.dashboard'))
```

E corrija a função `refresh_permanent_session`:

```python
@app.before_request
def refresh_permanent_session():
    try:
        if current_user and current_user.is_authenticated:
            session.permanent = True
            session.modified = True
    except Exception:
        pass
```

E corrija o callback do login_manager:

```python
@login_manager.user_loader
def carregar_usuario(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None
```

**Tempo:** 10 minutos

---

### Tarefa 2.3: Corrigir `models.py`

**Arquivo:** `models.py`

**Erro 1:** Corrigir `data_admissao`

```python
# ❌ ANTES (linha ~58):
data_admissao = db.Column(db.Date, default=date.today)

# ✅ DEPOIS:
data_admissao = db.Column(db.Date, default=lambda: date.today())
```

**Erro 2:** Corrigir relacionamentos da Empresa

```python
# ❌ ANTES:
admin = db.relationship("User", foreign_keys=[admin_id], backref="empresa_administradas")
users = db.relationship("User", backref="empresa", lazy=True, foreign_keys=lambda: [User.empresa_id])

# ✅ DEPOIS:
admin = db.relationship(
    "User", 
    foreign_keys=[admin_id], 
    backref="empresas_administradas"
)
users = db.relationship(
    "User", 
    backref="empresa_trabalho",
    lazy=True, 
    foreign_keys=lambda: [User.empresa_id]
)
```

**Tempo:** 10 minutos

---

### Tarefa 2.4: Implementar `calcular_horas_ponto()` em `utils.py`

**Arquivo:** `utils.py` 

Adicione esta função no final do arquivo (ou após `to_time`):

```python
def calcular_horas_ponto(ponto, carga=None):
    """
    Calcula horas trabalhadas, extras e deficits para um ponto (dia).
    
    Args:
        ponto: Objeto Ponto com marcações do dia
        carga: Timedelta com carga horária esperada (padrão: 8 horas)
    
    Returns:
        dict com total_trabalhado, extras, deficit
    """
    from models import Marcacao
    
    if carga is None:
        carga = timedelta(hours=8)
    
    marcacoes = Marcacao.query.filter_by(ponto_id=ponto.id)\
        .order_by(Marcacao.hora).all()
    
    if len(marcacoes) < 2:
        return {
            "total_trabalhado": timedelta(),
            "extras": timedelta(),
            "deficit": carga
        }
    
    entrada = to_time(ponto.data, marcacoes[0].hora)
    saida = to_time(ponto.data, marcacoes[-1].hora)
    
    pausa_almoco = timedelta()
    if len(marcacoes) > 2:
        saida_almoco = to_time(ponto.data, marcacoes[1].hora)
        retorno_almoco = to_time(ponto.data, marcacoes[2].hora)
        pausa_almoco = retorno_almoco - saida_almoco
    
    total_trabalhado = saida - entrada - pausa_almoco
    
    if total_trabalhado.total_seconds() < 0:
        total_trabalhado = timedelta()
    
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

**Tempo:** 15 minutos

---

### Tarefa 2.5: Corrigir `utils.py` - Decorator e Log

**Arquivo:** `utils.py`

**Erro 1:** Adicionar `@wraps` ao decorator

```python
# ❌ ANTES:
def admin_required(func):
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# ✅ DEPOIS:
def admin_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    return wrapper
```

**Erro 2:** Corrigir `log_action`

```python
# ❌ ANTES:
def log_action(usuario, acao):
    novo_log = Log(usuario_id=usuario.id, acao=acao)
    db.session.add(novo_log)
    db.session.commit()

# ✅ DEPOIS:
def log_action(usuario, acao):
    novo_log = Log(user_id=usuario.id, acao=acao)
    db.session.add(novo_log)
    db.session.commit()
```

**Tempo:** 5 minutos

---

### Tarefa 2.6: Validação em `auth/routes.py`

**Arquivo:** `auth/routes.py`

```python
# ❌ ANTES:
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        user = User.query.filter_by(email=email).first()

        if user and user.check_senha(senha):
            # ...
        else:
            flash("Usuário desconhecido. Contate o suporte.", "danger")

    return render_template("login.html")

# ✅ DEPOIS:
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()
        
        if not email or not senha:
            flash("Email e senha são obrigatórios", "danger")
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
            flash("Email ou senha incorretos", "danger")

    return render_template("login.html")
```

**Tempo:** 10 minutos

---

### Tarefa 2.7: Corrigir Dashboard do Admin

**Arquivo:** `routes/admin/dashboard.py`

```python
# ❌ ANTES:
funcionarios = User.query.filter_by(empresa_id=current_user.empresa_id, tipo="funcionario").all()

# ✅ DEPOIS:
funcionarios = User.query.filter_by(
    empresa_id=current_user.empresa_id, 
    tipo="funcionario",
    ativo=True
).all()
```

**Tempo:** 5 minutos

---

## ✅ Fase 2 - Checklist

- [ ] `.env` criado com valores seguros
- [ ] `.gitignore` criado
- [ ] `config.py` corrigido (sem padrões hardcoded)
- [ ] `app.py` corrigido (login_manager, error handlers, session)
- [ ] `models.py` corrigido (data_admissao, relacionamentos)
- [ ] `calcular_horas_ponto()` implementada em `utils.py`
- [ ] Decorators e log_action corrigidos em `utils.py`
- [ ] Validação adicionada em `auth/routes.py`
- [ ] Dashboard do admin filtrado por `ativo=True`
- [ ] App iniciado sem ImportError/AttributeError

**Tempo Total Fase 2:** ~60 minutos

---

## 🟠 Fase 3: Corrigir Altos (Segurança) - Próximos Dias

Após Fase 2 funcionar:

### 3.1: Adicionar CSRF Protection
```bash
pip install Flask-WTF
```

### 3.2: Adicionar Rate Limiting
```bash
pip install Flask-Limiter
```

### 3.3: Adicionar Logging Adequado
```bash
pip install python-logging-loki  # ou similar
```

### 3.4: Validação em Todos os Endpoints
- Usar WTForms ou Marshmallow
- Validar tipos de dados
- Validar ranges de valores

### 3.5: Audit Trail
- Log todas operações críticas
- Rastrear quem fez o quê e quando

---

## 🟡 Fase 4: Melhorias (Code Quality)

- Type hints em todas funções
- Docstrings completas
- Testes unitários
- Refatorar código duplicado

---

## 🧪 Testes Rápidos Após Cada Fase

### Teste 1: Verificar se inicia sem erro
```bash
python app.py
# Não deve haver ImportError, AttributeError, ValueError
```

### Teste 2: Login funciona
- Abra http://localhost:5000
- Tente fazer login com usuário válido

### Teste 3: Dashboard carrega
- Após login, deve carregar dashboard sem erro

---

## 📞 Se Algo Não Funcionar

1. Leia o erro completo
2. Procure pelo número de linha no arquivo
3. Compare com o código antes/depois em `GUIA_CORRECOES.md`
4. Verifique se `.env` tem todos os valores necessários
5. Tente `python -c "from models import *"` para detectar imports

---

## 📊 Progresso Esperado

| Fase | Tarefas | Tempo | Resultado |
|------|---------|-------|-----------|
| 1 | Setup .env, .gitignore | 30 min | App detecta config via .env |
| 2 | Corrigir 7 críticos | 60 min | App inicia e login funciona |
| 3 | Segurança | 8 horas | App seguro contra ataques comuns |
| 4 | Qualidade | 8 horas | Código profissional com testes |

**Total:** 1-2 semanas de trabalho focado

---

## 🎯 Meta Final

Seu app deve:

- ✅ Iniciar sem erros
- ✅ Login funciona
- ✅ Dashboard carrega dados corretos
- ✅ Sem exposição de credenciais
- ✅ Validação de inputs
- ✅ Error handling completo
- ✅ Logging de ações críticas
- ✅ Pronto para produção

---

## 📚 Referências

- **ANALISE_ERROS_COMPLETA.md** - Todos os 53 erros detalhados
- **GUIA_CORRECOES.md** - Código antes/depois
- **TABELA_REFERENCIA.md** - Referência rápida
- **.env.example** - Template de variáveis

