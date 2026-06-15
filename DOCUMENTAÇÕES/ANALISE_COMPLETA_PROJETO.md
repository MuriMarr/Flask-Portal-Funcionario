# 🔍 ANÁLISE COMPLETA DO PROJETO FLASK - Portal do Funcionário

**Data:** 2026-06-12  
**Status:** ⚠️ MÚLTIPLOS PROBLEMAS CRÍTICOS IDENTIFICADOS

---

## 📊 RESUMO EXECUTIVO

| Severidade | Qtd | Status |
|-----------|-----|--------|
| 🔴 CRÍTICO | 18 | Falhas de funcionalidade |
| 🟠 ALTO | 12 | Riscos de segurança/lógica |
| 🟡 MÉDIO | 15 | Code smells/boas práticas |
| 🟢 BAIXO | 8 | Melhorias futuras |
| **TOTAL** | **53** | **Encontrados** |

---

## 🔴 ERROS CRÍTICOS (Impedem funcionamento)

### 1. **app.py - Linha 12: Chave Secreta Hardcoded**
- **Arquivo:** [app.py](app.py#L12)
- **Código:** `CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN', 'admin@1234')`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Credencial de admin em código
- **Risco:** Qualquer pessoa pode autenticar como admin
- **Recomendação:** 
  ```python
  # Remover fallback ou usar valor aleatório
  CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN')
  if not CHAVE_SECRETA_ADMIN:
      raise ValueError("CHAVE_SECRETA_ADMIN não configurada no ambiente")
  ```

---

### 2. **app.py - Linha 67: Debug Mode Ativado em Produção**
- **Arquivo:** [app.py](app.py#L67)
- **Código:** `app.run(debug=True)`
- **Severidade:** 🔴 CRÍTICO (produção) | 🟡 MÉDIO (desenvolvimento)
- **Problema:** Debug mode ativa reloader e expõe erro detalhados
- **Risco:** Exposição de stack traces, código-fonte, variáveis
- **Recomendação:**
  ```python
  app.run(debug=os.environ.get('FLASK_ENV') == 'development')
  ```

---

### 3. **config.py - Linha 5: Credenciais de Banco Hardcoded**
- **Arquivo:** [config.py](config.py#L5)
- **Código:** `SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql+psycopg2://postgres:13954@localhost:5432/portal_funcionario')`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Senha do PostgreSQL visível no código
- **Risco:** Acesso não autorizado ao banco de dados
- **Recomendação:**
  ```python
  SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
  if not SQLALCHEMY_DATABASE_URI:
      raise ValueError("DATABASE_URL não configurada")
  ```

---

### 4. **auth/routes.py - Linha 79: Erro de Sintaxe em Flash**
- **Arquivo:** [auth/routes.py](auth/routes.py#L79)
- **Código:** `flash('Preencha todos os campos obrigatórios!' 'warning')`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Falta vírgula entre argumentos - TypeError
- **Recomendação:**
  ```python
  flash('Preencha todos os campos obrigatórios!', 'warning')
  ```

---

### 5. **utils.py - Linha 14: Parâmetro Incorreto em log_action**
- **Arquivo:** [utils.py](utils.py#L14)
- **Código:** `def log_action(usuario, acao):`  
  `novo_log = Log(usuario_id=usuario.id, acao=acao)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Função recebe `usuario` mas trata como User object - em [superadmin/ativacao.py](routes/superadmin/ativacao.py#L63) é chamada com string
- **Erro:** `AttributeError: 'str' object has no attribute 'id'`
- **Recomendação:**
  ```python
  def log_action(usuario_id, acao):
      novo_log = Log(user_id=usuario_id, acao=acao)
      db.session.add(novo_log)
      db.session.commit()
  ```

---

### 6. **utils.py - Linha 193: Campo Inexistente em Model**
- **Arquivo:** [utils.py](utils.py#L193)
- **Código:** `dias_gozados = sum(f.ferias_dias for f in funcionario.ferias if f.status == "concedida")`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** `Ferias` model não tem campo `ferias_dias`, tem `dias`
- **Erro:** `AttributeError: 'Ferias' object has no attribute 'ferias_dias'`
- **Recomendação:**
  ```python
  dias_gozados = sum(f.dias for f in funcionario.ferias if f.status == "aprovado")
  ```

---

### 7. **admin/dashboard.py - Linha 29: Atributo Incorreto**
- **Arquivo:** [routes/admin/dashboard.py](routes/admin/dashboard.py#L29)
- **Código:** `Ponto.query.join(User).filter(User.empresa_id == current_user.empresa_id)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Falta explicitação de `user_id` em Ponto - SQLAlchemy não consegue fazer JOIN automático
- **Erro:** `InvalidRequestError`
- **Recomendação:**
  ```python
  registros = Ponto.query.join(User, Ponto.user_id == User.id)\
      .filter(User.empresa_id == current_user.empresa_id).all()
  ```

---

### 8. **funcionarios/dashboard.py - Linha 11: Import Faltante**
- **Arquivo:** [routes/funcionarios/dashboard.py](routes/funcionarios/dashboard.py#L11)
- **Código:** `from utils import calcular_horas_ponto` (NÃO IMPORTADO)
- **Severidade:** 🔴 CRÍTICO
- **Erro:** `NameError: name 'calcular_horas_ponto' is not defined`
- **Recomendação:** Adicionar import em utils.py ou criar a função faltante

---

### 9. **relatorios/relatorio.py - Linha 10: Import Faltante**
- **Arquivo:** [routes/relatorios/relatorio.py](routes/relatorios/relatorio.py#L10)
- **Código:** `from utils import calcular_horas_ponto` (NÃO IMPORTADO)
- **Severidade:** 🔴 CRÍTICO
- **Erro:** `NameError: name 'calcular_horas_ponto' is not defined`
- **Recomendação:** Adicionar import

---

### 10. **documentos/documentos.py - Linha 6: Import Incorreto**
- **Arquivo:** [routes/documentos/documentos.py](routes/documentos/documentos.py#L6)
- **Código:** `from routes import admin_bp, funcionarios_bp`
- **Severidade:** 🔴 CRÍTICO
- **Erro:** Circular import ou módulo não encontrado
- **Recomendação:**
  ```python
  from routes.admin import admin_bp
  from routes.funcionarios import funcionarios_bp
  ```

---

### 11. **documentos/documentos.py - Linha 34: Assinatura de Função Incorreta**
- **Arquivo:** [routes/documentos/documentos.py](routes/documentos/documentos.py#L34)
- **Código:** `ferias_calc = calcular_pagamento_ferias(funcionario=funcionario, ferias=ferias, adiantamento_decimo=...)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Função em utils.py espera `(funcionario, dias=30, adiantamento_decimo=False)` não `ferias`
- **Erro:** `TypeError: unexpected keyword argument`
- **Recomendação:**
  ```python
  ferias_calc = calcular_pagamento_ferias(
      funcionario, 
      dias=ferias.dias,
      adiantamento_decimo=ferias.adiantamento_decimo
  )
  ```

---

### 12. **documentos/documentos.py - Linha 100: Reutilização de Variável**
- **Arquivo:** [routes/documentos/documentos.py](routes/documentos/documentos.py#L100)
- **Código:** `def holerite(user_id=None):` ... `pdf = gerar_pdf(..., holerite=holerite, ...)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** `holerite` é função, sendo passada como parâmetro de template
- **Erro:** Valor incorreto para template
- **Recomendação:**
  ```python
  pdf = gerar_pdf(..., mes=f"{ano}-{mes:02d}", ...)
  ```

---

### 13. **admin/ferias.py - Linha 16: Nome de Campo Incorreto**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L16)
- **Código:** `dias_trabalhados = (datetime.now().date() - funcionario.date_admissao).days`
- **Severidade:** 🔴 CRÍTICO
- **Erro:** `AttributeError: User has no attribute 'date_admissao'` (é `data_admissao`)
- **Recomendação:**
  ```python
  dias_trabalhados = (datetime.now().date() - funcionario.data_admissao).days
  ```

---

### 14. **admin/ferias.py - Linha 31: Rota Malformada**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L31)
- **Código:** `@admin_bp.route("ferias/<int:usuario_id>/editar/<int:ferias_id>")`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Falta `/` no início da rota
- **Recomendação:**
  ```python
  @admin_bp.route("/ferias/<int:usuario_id>/editar/<int:ferias_id>")
  ```

---

### 15. **admin/ferias.py - Linha 67: Nome de Campo Incorreto**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L67)
- **Código:** `ferias.data_fim = request.form.get("fim")`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Campo é `fim` não `data_fim` em models.py
- **Erro:** `AttributeError`
- **Recomendação:**
  ```python
  ferias.fim = request.form.get("fim")
  ferias.inicio = request.form.get("inicio")
  ```

---

### 16. **admin/ferias.py - Linha 98: Função Não Importada**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L98)
- **Código:** `return render_pdf(HTML(string=rendered), ...)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** `render_pdf` não é importado, e Flask-WeasyPrint não está em requirements.txt
- **Erro:** `NameError` e `ModuleNotFoundError`
- **Recomendação:**
  ```python
  from routes.common.pdf_utils import gerar_pdf
  
  # Usar gerar_pdf ao invés de render_pdf
  pdf = gerar_pdf("ferias_pdf.html", ...)
  ```

---

### 17. **admin/ferias.py - Linha 122: Campos Inexistentes**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L122-L130)
- **Código:** 
  ```python
  nova_ferias = Ferias(
      funcionario_id=funcionario.id,
      bruto=ferias_calc["bruto"],  # Campo não existe!
      desconto_inss=ferias_calc["desconto_inss"],  # Campo não existe!
      ...
  )
  ```
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Campos não definidos em modelo Ferias
- **Erro:** `TypeError: Ferias() got unexpected keyword argument`
- **Recomendação:**
  ```python
  nova_ferias = Ferias(
      funcionario_id=funcionario.id,
      inicio=inicio,
      fim=fim,
      dias=dias,
      adiantamento_decimo=adiantamento_decimo,
      status="aprovado"
  )
  ```

---

### 18. **admin/ponto.py - Linha 28: Nome de Coluna Incorreto**
- **Arquivo:** [routes/admin/ponto.py](routes/admin/ponto.py#L28)
- **Código:** `.filter(Ponto.usuario_id == usuario_id, ...)`
- **Severidade:** 🔴 CRÍTICO
- **Problema:** Coluna é `user_id` não `usuario_id`
- **Erro:** `AttributeError: Ponto has no attribute 'usuario_id'`
- **Recomendação:**
  ```python
  .filter(Ponto.user_id == usuario_id, ...)
  ```

---

## 🟠 ERROS DE ALTO RISCO (Segurança/Lógica)

### 19. **auth/routes.py - Linha 79: Validação Inadequada de Tipo de Usuário**
- **Arquivo:** [auth/routes.py](auth/routes.py#L79)
- **Código:** `tipo = request.form.get('tipo', 'funcionario')`
- **Severidade:** 🟠 ALTO
- **Problema:** Cliente controla tipo de usuário sem validação - privilege escalation
- **Risco:** Usuário pode se registrar como 'admin' ou 'superadmin'
- **Recomendação:**
  ```python
  # Sempre criar como funcionário
  tipo = 'funcionario'  # Nunca do request
  ```

---

### 20. **auth/routes.py - Linha 65: Missing Email Validation**
- **Arquivo:** [auth/routes.py](auth/routes.py#L65-L75)
- **Código:** `email = request.form.get("email", "").strip().lower()`
- **Severidade:** 🟠 ALTO
- **Problema:** Sem validação de formato de email
- **Risco:** Emails inválidos no banco
- **Recomendação:**
  ```python
  import re
  email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
  if not re.match(email_pattern, email):
      flash('Email inválido', 'danger')
      return redirect(...)
  ```

---

### 21. **admin/dashboard.py - Linha 18: Missing Authorization Check**
- **Arquivo:** [routes/admin/dashboard.py](routes/admin/dashboard.py#L18)
- **Código:** `funcionarios = User.query.filter_by(empresa_id=current_user.empresa_id, tipo="funcionario").all()`
- **Severidade:** 🟠 ALTO
- **Problema:** Sem verificar se current_user é admin da empresa_id
- **Risco:** Acesso não autorizado a dados de outras empresas
- **Recomendação:**
  ```python
  if current_user.tipo != 'admin' or current_user.empresa_id is None:
      abort(403)
  # ... resto do código
  ```

---

### 22. **superadmin/ativacao.py - Linha 63: Chamada com Argumentos Errados**
- **Arquivo:** [routes/superadmin/ativacao.py](routes/superadmin/ativacao.py#L63)
- **Código:** `log_action(request.environ.get("REMOTE_USER", "sistema"), f"Novo superadmin criado: {nome} para {empresa.razao_social}")`
- **Severidade:** 🟠 ALTO
- **Problema:** `log_action` espera User object mas recebe string
- **Erro:** `AttributeError`
- **Recomendação:** Refatorar `log_action` como mostrado em erro #5

---

### 23. **superadmin/ativacao.py - Linha 51: CPF Hardcoded**
- **Arquivo:** [routes/superadmin/ativacao.py](routes/superadmin/ativacao.py#L51)
- **Código:** `cpf="000.000.000-00",`
- **Severidade:** 🟠 ALTO
- **Problema:** CPF fake - duplicado para múltiplos superadmins
- **Risco:** Validações baseadas em CPF falharão
- **Recomendação:**
  ```python
  cpf=request.form.get("cpf", ""),  # Solicitar do usuário
  ```

---

### 24. **empresas/ativacao.py - Linha 26: Missing Permission Check**
- **Arquivo:** [routes/empresas/ativacao.py](routes/empresas/ativacao.py#L26-L31)
- **Código:** Rota pública sem verificar permissões antes
- **Severidade:** 🟠 ALTO
- **Problema:** Qualquer pessoa pode ativar empresa
- **Risco:** Criação não autorizada de contas
- **Recomendação:**
  ```python
  @login_required
  @superadmin_required  # Só superadmin pode ativar
  def ativacao(empresa_id):
  ```

---

### 25. **documentos/documentos.py - Linha 100: Missing Route Decorator**
- **Arquivo:** [routes/documentos/documentos.py](routes/documentos/documentos.py#L100)
- **Código:** `def holerite(user_id=None):` - SEM `@admin_bp.route(...)`
- **Severidade:** 🟠 ALTO
- **Problema:** Função não é acessível como rota
- **Recomendação:**
  ```python
  @admin_bp.route('/holerite/<int:user_id>')
  @funcionarios_bp.route('/holerite')
  @login_required
  def holerite(user_id=None):
  ```

---

### 26. **models.py - Linha 71: Ambiguous Relationship**
- **Arquivo:** [models.py](models.py#L71)
- **Código:** `users = db.relationship("User", backref="empresa", lazy=True, foreign_keys=lambda: [User.empresa_id])`
- **Severidade:** 🟠 ALTO
- **Problema:** Foreign_keys com lambda pode causar problemas em migrações
- **Recomendação:**
  ```python
  users = db.relationship("User", backref="empresa", lazy="select")
  # Remover foreign_keys lambda
  ```

---

### 27. **admin/ferias.py - Linha 78: Inconsistent Redirect**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L78)
- **Código:** `return redirect("admin.ferias_funcionario", usuario_id=usuario_id)` - ERRO
- **Severidade:** 🟠 ALTO
- **Problema:** `redirect()` espera URL, não nome de rota
- **Recomendação:**
  ```python
  return redirect(url_for("admin.ferias_funcionario", usuario_id=usuario_id))
  ```

---

### 28. **relatorios/relatorio_financeiro.py - Linha 18: Invalid DB Query**
- **Arquivo:** [routes/relatorios/relatorio_financeiro.py](routes/relatorios/relatorio_financeiro.py#L18-L21)
- **Código:** 
  ```python
  marcacoes = Marcacao.query.filter(
      db.extract('month', Marcacao.data) == mes,
      db.extract('year', Marcacao.data) == ano,
      Marcacao.user_id == f.id
  ).all()
  ```
- **Severidade:** 🟠 ALTO
- **Problema:** `Marcacao` não tem `user_id`, tem `ponto_id`. Precisa JOIN
- **Erro:** `AttributeError`
- **Recomendação:**
  ```python
  from sqlalchemy import and_
  marcacoes = Marcacao.query.join(Ponto).filter(
      and_(
          db.extract('month', Marcacao.data) == mes,
          db.extract('year', Marcacao.data) == ano,
          Ponto.user_id == f.id
      )
  ).all()
  ```

---

### 29. **relatorios/relatorio_financeiro.py - Linha 23-25: Invalid Attributes**
- **Arquivo:** [routes/relatorios/relatorio_financeiro.py](routes/relatorios/relatorio_financeiro.py#L23-L25)
- **Código:**
  ```python
  horas_trabalhadas = sum([m.total_horas for m in marcacoes if m.total_horas], 0)
  horas_extras = sum([m.extras for m in marcacoes if m.extras], 0)
  ```
- **Severidade:** 🟠 ALTO
- **Problema:** `Marcacao` não tem `total_horas` ou `extras`
- **Erro:** `AttributeError`
- **Recomendação:** Implementar `calcular_horas_ponto` ou criar atributo computado

---

### 30. **admin/ferias.py - Linha 52: String Assignment Instead of Date**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L52-L54)
- **Código:**
  ```python
  ferias.inicio = request.form.get("inicio")  # String!
  ferias.fim = request.form.get("fim")  # String!
  ferias.dias = request.form.get("dias")  # String!
  ```
- **Severidade:** 🟠 ALTO
- **Problema:** Atribuindo strings a campos de Data/Integer
- **Erro:** Validação ou casting incorreto
- **Recomendação:**
  ```python
  ferias.inicio = datetime.strptime(request.form.get("inicio"), "%Y-%m-%d").date()
  ferias.fim = datetime.strptime(request.form.get("fim"), "%Y-%m-%d").date()
  ferias.dias = int(request.form.get("dias"))
  ```

---

## 🟡 ERROS MÉDIOS (Code Smells/Boas Práticas)

### 31. **utils.py - Linha 3: Missing @wraps Decorator**
- **Arquivo:** [utils.py](utils.py#L3)
- **Código:** 
  ```python
  def admin_required(func):
      def wrapper(*args, **kwargs):
          # ...
      wrapper.__name__ = func.__name__  # Apenas __name__ copiado
      return wrapper
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Não copia metadata completa da função (docstring, etc)
- **Recomendação:**
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

### 32. **config.py - Linha 13: Side Effects em Módulo Config**
- **Arquivo:** [config.py](config.py#L13)
- **Código:** `os.makedirs(UPLOAD_FOLDER, exist_ok=True)`
- **Severidade:** 🟡 MÉDIO
- **Problema:** Executa lado-effect ao importar módulo
- **Recomendação:** Mover para `app.py` ou função separada
  ```python
  # Em app.py
  def create_app():
      app = Flask(__name__)
      app.config.from_object(Config)
      os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
      # ...
  ```

---

### 33. **models.py - Linha 48: Falta Índice em CPF/Email**
- **Arquivo:** [models.py](models.py#L48-L49)
- **Código:** 
  ```python
  cpf = db.Column(db.String(14), unique=True, nullable=False)
  email = db.Column(db.String(100), unique=True, nullable=False)
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Sem `index=True` - queries lentas
- **Recomendação:**
  ```python
  cpf = db.Column(db.String(14), unique=True, nullable=False, index=True)
  email = db.Column(db.String(100), unique=True, nullable=False, index=True)
  ```

---

### 34. **models.py - Linha 71-72: Ambiguous Foreign Key Relationship**
- **Arquivo:** [models.py](models.py#L71-L72)
- **Código:**
  ```python
  users = db.relationship("User", backref="empresa", lazy=True, foreign_keys=lambda: [User.empresa_id])
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Lambda para foreign_keys é desnecessário e pode quebrar
- **Recomendação:** Remover foreign_keys

---

### 35. **models.py - Linha 92-93: Relacionamento Circular**
- **Arquivo:** [models.py](models.py#L92-L93)
- **Código:**
  ```python
  pontos = db.relationship("Ponto", backref="user", cascade="all, delete-orphan", passive_deletes=True)
  logs = db.relationship("Log", backref="user", lazy=True)
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Cascade + passive_deletes pode causar comportamento inesperado
- **Recomendação:** Verificar se ambos são necessários

---

### 36. **auth/routes.py - Linha 88: Type Coercion Sem Validação**
- **Arquivo:** [auth/routes.py](auth/routes.py#L88)
- **Código:**
  ```python
  try:
      salario_mensal = float(request.form['salario_mensal'] or 0)
  except ValueError:
      salario_mensal = 1940.00
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Silenciosamente usa valor padrão sem notificar usuário
- **Recomendação:**
  ```python
  try:
      salario_mensal = float(request.form.get('salario_mensal') or 0)
  except ValueError:
      flash('Salário inválido', 'warning')
      return redirect(url_for('auth.registrar_funcionario'))
  ```

---

### 37. **admin/funcionarios.py - Linha 75: Date sem Timezone**
- **Arquivo:** [routes/admin/funcionarios.py](routes/admin/funcionarios.py#L75)
- **Código:** `data_admissao = datetime.now(timezone.utc),`
- **Severidade:** 🟡 MÉDIO
- **Problema:** Model espera `.date()` mas recebe `datetime`
- **Recomendação:**
  ```python
  data_admissao = datetime.now(timezone.utc).date(),
  ```

---

### 38. **admin/funcionarios.py - Linha 48-54: Validação Fora de Ordem**
- **Arquivo:** [routes/admin/funcionarios.py](routes/admin/funcionarios.py#L48-L54)
- **Código:** Valida CPF APÓS tentar usar em query
- **Severidade:** 🟡 MÉDIO
- **Problema:** Ordem lógica invertida
- **Recomendação:** Validar antes de usar

---

### 39. **admin/ferias.py - Linha 36: Redirect Sem url_for**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py#L36)
- **Código:** `return redirect("admin.ferias_funcionario", usuario_id=usuario_id)`
- **Severidade:** 🟡 MÉDIO
- **Problema:** Deve ser `url_for("admin.ferias_funcionario", ...)`
- **Recomendação:** Usar `url_for()`

---

### 40. **admin/ponto.py - Linha 16: Atributo Não Definido**
- **Arquivo:** [routes/admin/ponto.py](routes/admin/ponto.py#L16)
- **Código:** `.filter(Ponto.usuario_id == usuario_id, ...)`
- **Severidade:** 🟡 MÉDIO
- **Problema:** Coluna não existe, deve ser `user_id`
- **Recomendação:** Corrigir para `user_id`

---

### 41. **documentos/documentos.py - Linha 118: Header Duplicado**
- **Arquivo:** [routes/documentos/documentos.py](routes/documentos/documentos.py#L116-L118)
- **Código:**
  ```python
  response.headers['Content-Type'] = 'application/pdf'
  response.headers['Content-Type'] = f"inline; filename=ferias_{ferias.id}.pdf"
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Segundo atribui-se sobrescreve o primeiro
- **Recomendação:**
  ```python
  response.headers['Content-Type'] = 'application/pdf'
  response.headers['Content-Disposition'] = f'inline; filename=ferias_{ferias.id}.pdf'
  ```

---

### 42. **admin/funcionarios.py - Linha 72-81: Conversão Condicional Confusa**
- **Arquivo:** [routes/admin/funcionarios.py](routes/admin/funcionarios.py#L72-L81)
- **Código:**
  ```python
  if raw_salario:
      try:
          salario = float(raw_salario)
      except ValueError:
          flash("valor de salário inválido, Corrija e tente novamente", "danger")
          return redirect(url_for("admin.novo_funcionario"))
      else:
          flash("Salário não informado.", "warning")
  ```
- **Severidade:** 🟡 MÉDIO
- **Problema:** Lógica invertida - `else` executado se conversion bem-sucedida
- **Recomendação:**
  ```python
  if not raw_salario:
      flash("Salário não informado.", "warning")
      salario = 0.0
  else:
      try:
          salario = float(raw_salario)
      except ValueError:
          flash("Salário inválido.", "danger")
          return redirect(url_for("admin.novo_funcionario"))
  ```

---

### 43. **relatorios/relatorio_financeiro.py - Linha 22: Atributo Não Existe**
- **Arquivo:** [routes/relatorios/relatorio_financeiro.py](routes/relatorios/relatorio_financeiro.py#L22)
- **Código:** `f.salario` deve ser `f.salario_mensal`
- **Severidade:** 🟡 MÉDIO
- **Problema:** AttributeError
- **Recomendação:** `salario_base = f.salario_mensal or 0`

---

### 44. **requirements.txt - Dependência Faltante**
- **Arquivo:** [requirements.txt](requirements.txt)
- **Código:** `Flask-WeasyPrint` NÃO EXISTE
- **Severidade:** 🟡 MÉDIO
- **Problema:** Código usa `from flask_weasyprint import HTML, render_pdf` mas package não instalado
- **Recomendação:** Adicionar ao requirements.txt
  ```
  Flask-WeasyPrint==1.1.0
  weasyprint==62.3
  ```

---

### 45. **models.py - Falta CSRF Token**
- **Arquivo:** [models.py](models.py)
- **Severidade:** 🟡 MÉDIO
- **Problema:** Sem proteção CSRF em Flask-Login
- **Recomendação:** Adicionar Flask-WTF

---

## 🟢 ERROS BAIXOS (Melhorias)

### 46. **utils.py - Linha 143: Tratamento de None**
- **Arquivo:** [utils.py](utils.py#L143)
- **Código:** `if h:` mas não trata `-` em try/except
- **Severidade:** 🟢 BAIXO
- **Recomendação:** Melhorar tratamento

---

### 47. **extensions.py - Login View Sem Namespace**
- **Arquivo:** [extensions.py](extensions.py#L7)
- **Código:** `login_manager.login_view = 'auth.login'`
- **Severidade:** 🟢 BAIXO
- **Recomendação:** Adicionar `login_message`

---

### 48. **models.py - Campo Nullable Inconsistente**
- **Arquivo:** [models.py](models.py)
- **Severidade:** 🟢 BAIXO
- **Problema:** Alguns campos que deveriam ser NOT NULL permitem NULL
- **Recomendação:** Revisar constraints

---

### 49. **admin/ferias.py - String Formatting**
- **Arquivo:** [routes/admin/ferias.py](routes/admin/ferias.py)
- **Código:** Usar f-strings ao invés de `.format()`
- **Severidade:** 🟢 BAIXO

---

### 50. **models.py - Falta Documentação**
- **Arquivo:** [models.py](models.py)
- **Severidade:** 🟢 BAIXO
- **Problema:** Sem docstrings nos modelos
- **Recomendação:** Adicionar docstrings

---

### 51. **utils.py - Parâmetros Duplicados**
- **Arquivo:** [utils.py](utils.py#L143)
- **Código:** `if isinstance(value, timedelta)` e depois `if value is None`
- **Severidade:** 🟢 BAIXO
- **Recomendação:** Refatorar ordem

---

### 52. **admin/dashboard.py - Cálculo Complexo**
- **Arquivo:** [routes/admin/dashboard.py](routes/admin/dashboard.py#L23-L27)
- **Severidade:** 🟢 BAIXO
- **Problema:** Lógica complexa para calcular horas
- **Recomendação:** Extrair em função

---

### 53. **Falta de Logging**
- **Arquivo:** Projeto inteiro
- **Severidade:** 🟢 BAIXO
- **Problema:** Sem logging estruturado (print statements podem existir)
- **Recomendação:** Implementar logging com `logging` module

---

## 📋 MATRIZ DE RISCOS

### Por Categoria:

| Categoria | CRÍTICO | ALTO | MÉDIO | BAIXO | Total |
|-----------|---------|------|-------|-------|-------|
| Erros de Sintaxe | 1 | 0 | 0 | 0 | 1 |
| Import/Módulo | 3 | 1 | 1 | 0 | 5 |
| Banco de Dados | 5 | 2 | 3 | 2 | 12 |
| Segurança | 2 | 4 | 2 | 0 | 8 |
| Lógica | 7 | 5 | 5 | 2 | 19 |
| Configuração | 2 | 0 | 2 | 0 | 4 |
| Boas Práticas | 0 | 0 | 2 | 3 | 5 |
| **TOTAL** | **18** | **12** | **15** | **8** | **53** |

---

## 🚀 PLANO DE AÇÃO PRIORIZADO

### Fase 1: CRÍTICO (Implementar Imediatamente - 24h)
1. Remover credenciais hardcoded (config.py, app.py)
2. Corrigir erros de sintaxe e imports
3. Corrigir atributos de model (user_id vs usuario_id, data_admissao vs date_admissao)
4. Corrigir assinatura de calcular_horas_ponto
5. Adicionar imports faltantes
6. Corrigir rotinas de PDF

### Fase 2: ALTO (24-48h)
1. Validação de tipo de usuário
2. Checks de autorização
3. Validação de email
4. Refatorar log_action
5. Corrigir relationshps e JOINs

### Fase 3: MÉDIO (48-72h)
1. Implementar @wraps
2. Adicionar índices
3. Adicionar Fleet-WeasyPrint a requirements
4. Melhorar tratamento de erros
5. Refatorar lógica complexa

### Fase 4: BAIXO (1-2 semanas)
1. Adicionar docstrings
2. Implementar logging
3. Code formatting
4. Testes unitários

---

## 🔐 RECOMENDAÇÕES DE SEGURANÇA

1. **Usar variáveis de ambiente** para todas credenciais
2. **Implementar CSRF protection** com Flask-WTF
3. **Validar todos inputs** com regex ou validators
4. **Usar prepared statements** (SQLAlchemy já faz)
5. **Implementar rate limiting** para login
6. **Auditar permissões** em todas rotas
7. **Criptografar dados sensíveis** (CPF, etc)
8. **Adicionar logging de segurança**
9. **Usar HTTPS em produção**
10. **Implementar 2FA para admins**

---

## 📝 CHECKLIST DE REVISÃO

- [ ] Todos os CRÍTICOS foram corrigidos
- [ ] Testes unitários implementados
- [ ] Testes de integração passando
- [ ] Segurança auditada
- [ ] Performance testada
- [ ] Documentação atualizada
- [ ] Credenciais removidas
- [ ] Logs implementados
- [ ] Code review completado
- [ ] Deploy em staging

---

**Análise Concluída em:** 2026-06-12  
**Próxima Revisão Recomendada:** Após correção dos erros CRÍTICOS
