# 🔍 ANÁLISE COMPLETA DE ERROS - Portal do Funcionário

## 📊 Resumo Executivo
- **Total de Problemas: 53**
- 🔴 **18 CRÍTICOS** (Impedem funcionamento)
- 🟠 **12 ALTOS** (Riscos de segurança/lógica)
- 🟡 **15 MÉDIOS** (Code smells/boas práticas)
- 🟢 **8 BAIXOS** (Melhorias futuras)

---

## 🔴 PROBLEMAS CRÍTICOS (Prioridade 1)

### 1. ❌ Credenciais Hardcoded no `config.py`
**Arquivo:** `config.py` (linha 6)  
**Severidade:** CRÍTICO  
**Problema:**
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:13954@localhost:5432/portal_funcionario')
```
- A senha do PostgreSQL (13954) está visível no código
- Qualquer pessoa com acesso ao repo terá acesso ao banco

**Solução:**
```python
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://user:password@localhost:5432/portal_funcionario')
# E definir DATABASE_URL no arquivo .env
```

---

### 2. ❌ Chave Secreta de Admin Hardcoded
**Arquivo:** `app.py` (linha 12)  
**Severidade:** CRÍTICO  
**Problema:**
```python
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN', 'admin@1234')
```
- Padrão é uma senha fraca e previsível
- Nunca deve estar no código

**Solução:**
```python
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN')
if not CHAVE_SECRETA_ADMIN:
    raise ValueError("CHAVE_SECRETA_ADMIN não configurada no .env")
```

---

### 3. ❌ Atributo `usuario_id` Não Existe nos Modelos
**Arquivos:** Múltiplos
**Severidade:** CRÍTICO  
**Problema:** O código usa `usuario_id` mas o modelo define `user_id`

**Locais encontrados:**
- `routes/admin/dashboard.py` - usa nomes incorretos de campos
- `routes/funcionarios/` - usa `usuario_id` em queries
- `routes/superadmin/` - mesmo problema
- `utils.py` - função `log_action` usa `usuario_id` (não existe)

**Solução:** Padronizar para `user_id` em TODO o código

```python
# ❌ ERRADO
novo_log = Log(usuario_id=usuario.id, acao=acao)

# ✅ CORRETO
novo_log = Log(user_id=usuario.id, acao=acao)
```

---

### 4. ❌ Função `calcular_horas_ponto()` Não Implementada
**Arquivo:** `utils.py`  
**Severidade:** CRÍTICO  
**Problema:** 
- Função é chamada em 3 arquivos diferentes
- Não existe em `utils.py`
- Causa erro em: `relatorios/relatorio.py` (linhas 23, 62), `admin/dashboard.py` (linha 20)

**Chamadas encontradas:**
```python
resultado = calcular_horas_ponto(p, carga=timedelta(hours=8))  # ❌ Função não existe!
```

**Solução:** Implementar a função em `utils.py`:
```python
def calcular_horas_ponto(ponto, carga=timedelta(hours=8)):
    """
    Calcula horas trabalhadas, extras e deficits para um dia
    
    Args:
        ponto: Objeto Ponto com marcações do dia
        carga: Carga horária esperada (padrão 8 horas)
    
    Returns:
        dict com total_trabalhado, extras, deficit
    """
    from models import Marcacao
    
    marcacoes = Marcacao.query.filter_by(ponto_id=ponto.id).order_by(Marcacao.hora).all()
    
    if len(marcacoes) < 2:
        return {
            "total_trabalhado": timedelta(),
            "extras": timedelta(),
            "deficit": carga
        }
    
    # Lógica de cálculo (entrada e saída, com pausa de almoço)
    entrada = to_time(ponto.data, marcacoes[0].hora)
    saida_almoco = to_time(ponto.data, marcacoes[1].hora)
    retorno_almoco = to_time(ponto.data, marcacoes[2].hora) if len(marcacoes) > 2 else None
    saida = to_time(ponto.data, marcacoes[-1].hora)
    
    if retorno_almoco:
        pausa_almoco = retorno_almoco - saida_almoco
    else:
        pausa_almoco = timedelta()
    
    total_trabalhado = saida - entrada - pausa_almoco
    
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

---

### 5. ❌ Erro de Sintaxe em `auth/routes.py`
**Arquivo:** `auth/routes.py` (linha 24)  
**Severidade:** CRÍTICO  
**Problema:**
```python
flash("Usuário desconhecido. Contate o suporte.", "danger")  # ❌ Falta erro de lógica
```

**Solução:** Mensagem deve ser mais específica:
```python
else:
    flash("Email ou senha incorretos", "danger")
```

---

### 6. ❌ Decorator `@wraps` Não Importado Corretamente
**Arquivo:** `utils.py` (linha 2)  
**Severidade:** CRÍTICO  
**Problema:** Em `admin_required()`, falta `@wraps`:

```python
def admin_required(func):
    def wrapper(*args, **kwargs):  # ❌ wrapper não preserva metadados
        if not current_user.is_authenticated or current_user.tipo not in ['admin', 'superadmin']:
            abort(403)
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__  # Gambiarra, deveria usar @wraps
    return wrapper
```

**Solução:**
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

### 7. ❌ Atributo `data_admissao` Incorreto
**Arquivo:** `models.py` (linha 58)  
**Severidade:** CRÍTICO  
**Problema:**
```python
data_admissao = db.Column(db.Date, default=date.today)  # ❌ Deveria ser date.today()
```
- Falta parênteses em `date.today`
- Isso causará erro ao inserir novos usuários

**Solução:**
```python
data_admissao = db.Column(db.Date, default=lambda: date.today())
```

---

### 8. ❌ Campo `usuario_id` em `Log` Model
**Arquivo:** `models.py` (linha 92)  
**Severidade:** CRÍTICO  
**Problema:**
```python
class Log(db.Model):
    # ...
    user_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
```
Mas em `utils.py` usa-se:
```python
novo_log = Log(usuario_id=usuario.id, acao=acao)  # ❌ usuario_id não existe!
```

**Solução:** Padronizar o nome do atributo

---

### 9. ❌ Relacionamento Circular Não Resolvido
**Arquivo:** `models.py` (linhas 18-19)  
**Severidade:** CRÍTICO  
**Problema:**
```python
admin = db.relationship("User", foreign_keys=[admin_id], backref="empresa_administradas")
users = db.relationship("User", backref="empresa", lazy=True, foreign_keys=lambda: [User.empresa_id])
```
- `backref="empresa"` em `Empresa` conflita com relacionamento reverso
- Causa ambiguidade no relacionamento

**Solução:**
```python
admin = db.relationship("User", foreign_keys=[admin_id], backref="empresas_administradas")
users = db.relationship("User", backref="empresa_trabalho", lazy=True, foreign_keys=lambda: [User.empresa_id])
```

---

### 10. ❌ Callback `carregar_usuario()` Não Trata Erro
**Arquivo:** `app.py` (linha 70)  
**Severidade:** CRÍTICO  
**Problema:**
```python
@login_manager.user_loader
def carregar_usuario(user_id):
    return User.query.get(int(user_id))  # Pode falhar se user_id não for número
```

**Solução:**
```python
@login_manager.user_loader
def carregar_usuario(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None
```

---

### 11. ❌ SESSION_PERMANENT Definido em Ambos os Lugares
**Arquivo:** `app.py` (linha 28) e `config.py` (linha 12)  
**Severidade:** CRÍTICO  
**Problema:** Comportamento indefinido - qual será aplicado?

**Solução:** Remover de `app.py`, deixar apenas em `config.py`

---

### 12. ❌ Falta Tratamento de Exceção em `refresh_permanent_session()`
**Arquivo:** `app.py` (linhas 25-27)  
**Severidade:** CRÍTICO  
**Problema:**
```python
@app.before_request
def refresh_permanent_session():
    if current_user and current_user.is_authenticated:  # ❌ current_user pode falhar
        session.permanent = True
        session.modified = True
```

**Solução:**
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

---

### 13. ❌ `SECRET_KEY` Fraco no `config.py`
**Arquivo:** `config.py` (linha 5)  
**Severidade:** CRÍTICO  
**Problema:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')
```
- Padrão é uma chave fraca ('dev-secret')
- Em produção, deve ser robusta

**Solução:**
```python
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY não configurada no .env")
```

---

### 14. ❌ Falta Validação em Route de Login
**Arquivo:** `auth/routes.py` (linhas 14-15)  
**Severidade:** CRÍTICO  
**Problema:**
```python
email = request.form.get("email")
senha = request.form.get("senha")
# Sem validação ou sanitização!
```

**Solução:** Adicionar validação:
```python
email = request.form.get("email", "").strip()
senha = request.form.get("senha", "").strip()

if not email or not senha:
    flash("Email e senha são obrigatórios", "danger")
    return render_template("login.html")
```

---

### 15. ❌ Query Não Filtra por Empresa Ativa
**Arquivo:** `routes/admin/dashboard.py` (linhas 11-12)  
**Severidade:** CRÍTICO  
**Problema:**
```python
funcionarios = User.query.filter_by(empresa_id=current_user.empresa_id, tipo="funcionario").all()
registros = Ponto.query.join(User).filter(User.empresa_id == current_user.empresa_id).all()
```
- Não filtra usuários inativos/demitidos
- Pode incluir dados de funcionários desligados

**Solução:**
```python
funcionarios = User.query.filter_by(
    empresa_id=current_user.empresa_id, 
    tipo="funcionario",
    ativo=True  # ✅ Adicionar filtro
).all()
```

---

### 16. ❌ Lógica de Cálculo Incorreta em Dashboard
**Arquivo:** `routes/admin/dashboard.py` (linhas 21-27)  
**Severidade:** CRÍTICO  
**Problema:**
```python
for r in registros:
    marcacoes = Marcacao.query.filter_by(ponto_id=r.id).order_by(Marcacao.hora).all()
    if len(marcacoes) >= 2:
        entrada = datetime.combine(r.data, marcacoes[0].hora)
        saida_almoco = datetime.combine(r.data, marcacoes[1].hora)
        retorno_almoco = datetime.combine(r.data, marcacoes[2].hora) if len(marcacoes) > 2 else None
        saida = datetime.combine(r.data, marcacoes[-1].hora)
        total_horas += (saida - entrada - (retorno_almoco - saida_almoco if retorno_almoco else timedelta()))
```

- Assume padrão fixo de marcações (entrada, saída almoço, entrada almoço, saída)
- Não valida se marcações seguem esse padrão
- Pode calcular negativos se marcações fora de ordem

**Solução:** Usar a função `calcular_horas_ponto()` genérica

---

### 17. ❌ Falta Paginação em Grandes Consultas
**Arquivo:** Múltiplos (relatorios, admin, superadmin)  
**Severidade:** CRÍTICO  
**Problema:**
```python
funcionarios = User.query.filter_by(tipo="funcionario").all()  # ❌ Sem limite
relatorio = []
for func in funcionarios:  # ❌ Loop N+1 queries
    pontos = Ponto.query.filter(...).all()
```

- Se houver 10k+ funcionários, carrega tudo na memória
- Causa N+1 query problem

**Solução:** Usar paginação:
```python
page = request.args.get('page', 1, type=int)
funcionarios = User.query.filter_by(tipo="funcionario").paginate(page=page, per_page=50)
```

---

### 18. ❌ Falta Validação em Dados de Formulário
**Arquivo:** Múltiplos formulários  
**Severidade:** CRÍTICO  
**Problema:** Nenhuma validação de dados antes de salvar no BD
- Datas podem estar em formato errado
- Números fora de range
- Campos obrigatórios vazios

---

---

## 🟠 PROBLEMAS ALTOS (Prioridade 2)

### 19. ❌ Falta CSRF Protection
**Severidade:** ALTO  
**Problema:** Formulários não possuem tokens CSRF

**Solução:**
```bash
pip install Flask-WTF
```

---

### 20. ❌ SQL Injection Potencial em Filtros Customizados
**Severidade:** ALTO  
**Problema:** Se há filtros por query string não sanitizados

---

### 21. ❌ Falta Rate Limiting em Login
**Severidade:** ALTO  
**Problema:** Nenhuma proteção contra brute force

**Solução:**
```bash
pip install Flask-Limiter
```

---

### 22. ❌ Senhas Não São Validadas na Criação
**Severidade:** ALTO  
**Problema:** Qualquer string é aceita como senha

---

### 23. ❌ Falta Audit Trail Completo
**Severidade:** ALTO  
**Problema:** Mudanças críticas não são registradas

---

### 24. ❌ Erro ao Deletar Usuário com Relacionamentos
**Severidade:** ALTO  
**Problema:** Cascade delete pode causar inconsistências

---

### 25. ❌ JSON Sem Validação
**Severidade:** ALTO  
**Problema:** Endpoints JSON aceitam dados sem schema

---

### 26. ❌ Falta Logging de Erros
**Severidade:** ALTO  
**Problema:** Erros não são registrados para debug

---

### 27. ❌ Arquivo de Upload Sem Validação
**Severidade:** ALTO  
**Problema:** Qualquer arquivo pode ser feito upload

---

### 28. ❌ Falta Tratamento de Exceções Global
**Severidade:** ALTO  
**Problema:** Erros 500 não são tratados

**Solução:**
```python
@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
```

---

### 29. ❌ Timezone Não Configurado Globalmente
**Severidade:** ALTO  
**Problema:** Usa `timezone.utc` em alguns lugares, naive em outros

---

### 30. ❌ Migração do Banco Pode Falhar
**Severidade:** ALTO  
**Problema:** Scripts de migração antigos podem não estar updated

---

---

## 🟡 PROBLEMAS MÉDIOS (Prioridade 3)

### 31. ❌ Imports Desorganizados
**Severidade:** MÉDIO  
**Problema:** Imports não seguem ordem PEP8

---

### 32. ❌ Código Duplicado em Relatórios
**Severidade:** MÉDIO  
**Problema:** `relatorio_jornada()` e `relatorio_jornada_pdf()` duplicam lógica

**Solução:** Extrair lógica comum

---

### 33. ❌ Variáveis com Nomes Genéricos
**Severidade:** MÉDIO  
**Problema:** `r`, `p`, `f` não são nomes descritivos

---

### 34. ❌ Falta Type Hints
**Severidade:** MÉDIO  
**Problema:** Funções sem anotações de tipo

---

### 35. ❌ Docstrings Faltando
**Severidade:** MÉDIO  
**Problema:** Funções sem documentação

---

### 36. ❌ Config Não Usa Classes Herança
**Severidade:** MÉDIO  
**Problema:** Deveria ter Dev, Test, Prod configs

---

### 37. ❌ URLs Hardcoded em Templates
**Severidade:** MÉDIO  
**Problema:** Deveria usar `url_for()`

---

### 38. ❌ Falta .gitignore
**Severidade:** MÉDIO  
**Problema:** .env pode ser commitado

---

### 39. ❌ Banco de Dados Local em Produção?
**Severidade:** MÉDIO  
**Problema:** Não está claro qual BD é usado em prod

---

### 40. ❌ Falta Testes Unitários
**Severidade:** MÉDIO  
**Problema:** Nenhum teste automático

---

### 41. ❌ Relacionamentos Bidirecionais Confusos
**Severidade:** MÉDIO  
**Problema:** Backrefs podem causar N+1 queries

---

### 42. ❌ Falta Validação de Email
**Severidade:** MÉDIO  
**Problema:** Qualquer string é aceita como email

---

### 43. ❌ Falta Formatação de Datas em Templates
**Severidade:** MÉDIO  
**Problema:** Datas podem aparecer em formato incorreto

---

### 44. ❌ Console de Erros Pode Expor Informações
**Severidade:** MÉDIO  
**Problema:** Debug=True em produção?

---

### 45. ❌ Falta Validação de Permissões em Todos os Endpoints
**Severidade:** MÉDIO  
**Problema:** Alguns endpoints podem não validar autorização

---

---

## 🟢 PROBLEMAS BAIXOS (Prioridade 4)

### 46. ❌ Espaçamento Inconsistente
### 47. ❌ Constantes Não Estão Centralizadas
### 48. ❌ Falta Informação de Versão
### 49. ❌ Banco Cria Tabelas com `db.create_all()` em Produção
### 50. ❌ Múltiplas Tabelas Sem Índices
### 51. ❌ Falta Backup/Restore Strategy
### 52. ❌ Descrição em README Vaga
### 53. ❌ Falta Plano de Escalabilidade

---

## 📋 Checklist de Correções Prioritárias

- [ ] Remover senhas hardcoded
- [ ] Implementar `calcular_horas_ponto()`
- [ ] Corrigir nomes de atributos (usuario_id → user_id)
- [ ] Corrigir `data_admissao` (faltam parênteses)
- [ ] Adicionar CSRF protection
- [ ] Adicionar validação de formulários
- [ ] Adicionar tratamento de exceções global
- [ ] Implementar rate limiting
- [ ] Adicionar logging
- [ ] Corrigir relacionamentos de modelos

---

## 🚀 Próximos Passos

1. **HOJE:** Corrigir os 10 primeiros CRÍTICOS
2. **AMANHÃ:** Corrigir erros de lógica (15-16)
3. **DIA 3:** Implementar segurança (ALTO)
4. **DIA 4:** Testes e deploy

