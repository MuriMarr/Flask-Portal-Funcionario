# 🔍 TABELA DE REFERÊNCIA RÁPIDA - Erros Encontrados

## Índice Rápido por Arquivo

| Arquivo | Linha | Erro | Tipo | Ação |
|---------|-------|------|------|------|
| **app.py** | 12 | Chave admin hardcoded | 🔴 CRÍTICO | Remover fallback |
| app.py | 67 | debug=True | 🔴 CRÍTICO | Usar variável ambiente |
| **config.py** | 5 | Senha no DATABASE_URL | 🔴 CRÍTICO | Mover para .env |
| config.py | 13 | os.makedirs em módulo | 🟡 MÉDIO | Mover para app.py |
| **models.py** | 48 | CPF sem índice | 🟡 MÉDIO | Adicionar index=True |
| models.py | 49 | Email sem índice | 🟡 MÉDIO | Adicionar index=True |
| models.py | 71 | foreign_keys lambda | 🟡 MÉDIO | Remover lambda |
| models.py | 92 | cascade+passive_deletes | 🟡 MÉDIO | Revisar ambos |
| **utils.py** | 3 | admin_required sem @wraps | 🟡 MÉDIO | Adicionar @wraps |
| utils.py | 14 | log_action parâmetro errado | 🔴 CRÍTICO | Receber user_id |
| utils.py | 193 | ferias_dias não existe | 🔴 CRÍTICO | Usar dias |
| **extensions.py** | 7 | Login message vazio | 🟢 BAIXO | Adicionar mensagem |
| **auth/routes.py** | 65 | Email sem validação | 🟠 ALTO | Validar regex |
| auth/routes.py | 79 | Erro de sintaxe | 🔴 CRÍTICO | Adicionar vírgula |
| auth/routes.py | 79 | tipo do request | 🟠 ALTO | Hardcoded 'funcionario' |
| auth/routes.py | 88 | Type coercion silencioso | 🟡 MÉDIO | Flash error |
| **admin/dashboard.py** | 18 | Missing auth check | 🟠 ALTO | Verificar empresa_id |
| admin/dashboard.py | 29 | JOIN ambíguo | 🔴 CRÍTICO | JOIN explícito |
| **admin/ferias.py** | 16 | date_admissao incorreto | 🔴 CRÍTICO | data_admissao |
| admin/ferias.py | 31 | Rota sem / | 🔴 CRÍTICO | Adicionar / |
| admin/ferias.py | 52 | String para Data | 🟠 ALTO | strptime antes |
| admin/ferias.py | 67 | data_fim não existe | 🔴 CRÍTICO | Usar fim |
| admin/ferias.py | 78 | redirect sem url_for | 🟡 MÉDIO | Usar url_for |
| admin/ferias.py | 98 | render_pdf não importa | 🔴 CRÍTICO | Usar gerar_pdf |
| admin/ferias.py | 122 | Campos inexistentes | 🔴 CRÍTICO | Remover campos |
| **admin/ponto.py** | 28 | usuario_id incorreto | 🔴 CRÍTICO | Usar user_id |
| **admin/funcionarios.py** | 48 | Validação fora ordem | 🟡 MÉDIO | Reordenar |
| admin/funcionarios.py | 72 | Lógica invertida | 🟡 MÉDIO | Refatorar if/else |
| admin/funcionarios.py | 75 | datetime.now() vs .date() | 🟡 MÉDIO | Adicionar .date() |
| **funcionarios/dashboard.py** | 11 | calcular_horas_ponto missing | 🔴 CRÍTICO | Implementar função |
| **funcionarios/ferias.py** | 18 | ferias_dias não existe | 🔴 CRÍTICO | Usar dias |
| **documentos/documentos.py** | 6 | Import errado | 🔴 CRÍTICO | Corrigir import |
| documentos/documentos.py | 34 | Assinatura errada | 🔴 CRÍTICO | Passar dias, não ferias |
| documentos/documentos.py | 100 | Sem @route decorator | 🟠 ALTO | Adicionar @route |
| documentos/documentos.py | 100 | holerite reutilizado | 🔴 CRÍTICO | Renomear variável |
| documentos/documentos.py | 116 | Header duplicado | 🟡 MÉDIO | Content-Disposition |
| **relatorios/relatorio.py** | 10 | calcular_horas_ponto missing | 🔴 CRÍTICO | Implementar/importar |
| **relatorios/relatorio_financeiro.py** | 18 | Query inválida | 🟠 ALTO | JOIN com Ponto |
| relatorios/relatorio_financeiro.py | 23 | total_horas não existe | 🟠 ALTO | Calcular corretamente |
| relatorios/relatorio_financeiro.py | 22 | f.salario incorreto | 🟡 MÉDIO | salario_mensal |
| **empresas/ativacao.py** | 26 | Missing permission | 🟠 ALTO | @superadmin_required |
| **superadmin/ativacao.py** | 51 | CPF hardcoded | 🟠 ALTO | Solicitar do usuário |
| superadmin/ativacao.py | 63 | log_action incorreto | 🔴 CRÍTICO | Passar user_id |
| **superadmin/dashboard.py** | 10 | Missing permission check | 🟡 MÉDIO | Verificar tipo |
| **requirements.txt** | - | Flask-WeasyPrint missing | 🟡 MÉDIO | Adicionar pacote |

---

## 📊 Sumário por Severidade

### 🔴 CRÍTICOS (18) - Corrigir HOJE

1. app.py:12 - Chave admin hardcoded
2. app.py:67 - debug=True
3. config.py:5 - Senha hardcoded
4. auth/routes.py:79 - Erro de sintaxe
5. utils.py:14 - log_action parâmetro
6. utils.py:193 - ferias_dias field
7. admin/dashboard.py:29 - JOIN ambíguo
8. admin/ferias.py:16 - date_admissao
9. admin/ferias.py:31 - Rota sem /
10. admin/ferias.py:67 - data_fim
11. admin/ferias.py:98 - render_pdf
12. admin/ferias.py:122 - Campos
13. admin/ponto.py:28 - usuario_id
14. funcionarios/dashboard.py:11 - calcular_horas_ponto
15. funcionarios/ferias.py:18 - ferias_dias
16. documentos/documentos.py:6 - Import
17. documentos/documentos.py:34 - Assinatura
18. documentos/documentos.py:100 - holerite var

### 🟠 ALTOS (12) - Corrigir Semana 1

1. auth/routes.py:65 - Email validation
2. auth/routes.py:79 - tipo escalation
3. admin/dashboard.py:18 - Auth check
4. admin/ferias.py:52 - Type coercion
5. empresas/ativacao.py:26 - Permission
6. documentos/documentos.py:100 - Missing @route
7. relatorios/relatorio.py:10 - calcular_horas_ponto
8. relatorios/relatorio_financeiro.py:18 - Query
9. relatorios/relatorio_financeiro.py:23 - Attributes
10. superadmin/ativacao.py:51 - CPF hardcoded
11. superadmin/ativacao.py:63 - log_action
12. [outros 1] - Verificação

### 🟡 MÉDIOS (15) - Corrigir Semana 2

1. config.py:13 - Side effects
2. models.py:48 - CPF index
3. models.py:49 - Email index
4. models.py:71 - foreign_keys
5. models.py:92 - cascade
6. utils.py:3 - @wraps
7. auth/routes.py:88 - Type coercion
8. admin/ferias.py:78 - redirect
9. admin/funcionarios.py:48 - Validação ordem
10. admin/funcionarios.py:72 - Lógica if/else
11. admin/funcionarios.py:75 - .date()
12. documentos/documentos.py:116 - Header
13. relatorios/relatorio_financeiro.py:22 - salario
14. superadmin/dashboard.py:10 - Permission
15. requirements.txt - Flask-WeasyPrint

### 🟢 BAIXOS (8) - Backlog

1. extensions.py:7 - Login message
2. utils.py - Tratamento None
3. models.py - Nullable inconsistente
4. admin/ferias.py - String formatting
5. models.py - Documentação
6. utils.py - Parâmetros duplicados
7. admin/dashboard.py - Cálculo complexo
8. Logging estruturado

---

## 🛠️ Ferramenta de Busca por Tipo

### Atributos de Modelo Incorretos
```
usuario_id → user_id (Ponto, Admin)
date_admissao → data_admissao (Admin Ferias)
ferias_dias → dias (Utils)
data_fim → fim (Admin Ferias)
f.salario → f.salario_mensal (Relatorios)
```

### Imports Faltantes
```
from utils import calcular_horas_ponto (3 arquivos)
from routes.admin import admin_bp (Documentos)
from functools import wraps (Utils)
@wraps decorator (Utils)
Flask-WeasyPrint (requirements.txt)
```

### Validações Faltantes
```
Email regex validation (Auth)
Type de usuário hardcoded (Auth)
Authorization checks (Admin, Superadmin)
Date parsing (Admin Ferias)
Autorização de empresa (Admin Dashboard)
```

### Problemas de Segurança
```
Chaves hardcoded (Config, App)
CSRF protection (Projeto todo)
SQL injection potencial (JOINs)
Escalação de privilégio (Registro)
CPF fake (Superadmin)
```

---

## ⚡ Quick Fix Checklist (45 minutos)

- [ ] (2 min) Adicionar vírgula em auth/routes.py:79
- [ ] (5 min) Adicionar @wraps em utils.py
- [ ] (10 min) Renomear usuario_id → user_id (3 arquivos)
- [ ] (10 min) Renomear date_admissao → data_admissao
- [ ] (5 min) Adicionar Flask-WeasyPrint a requirements.txt
- [ ] (8 min) Adicionar imports faltantes
- [ ] (5 min) Criar .env.example

---

## 🔗 Relacionamentos Entre Erros

```
Erro em database.py:5 (credencial)
  ↓
Precisa ser resolvido para app funcionar
  ↓
Erro em auth/routes.py:79 (sintaxe)
  ↓
Bloqueia login
  ↓
Impossível testar outros módulos

admin/dashboard.py:29 (JOIN)
  ↓
Precisa de calcular_horas_ponto
  ↓
Que está em utils.py (não importado)
  ↓
Bloqueia dashboard de admin
```

---

## 📈 Ordem de Correção Recomendada

**TOP 10 para começar:**

1. config.py:5 - Remover senha (5 min)
2. app.py:12 - Remover chave (2 min)
3. auth/routes.py:79 - Vírgula (2 min)
4. utils.py - Implementar calcular_horas_ponto (20 min)
5. Renomear user_id em 3 arquivos (15 min)
6. Renomear data_admissao (10 min)
7. Adicionar imports (10 min)
8. Corrigir admin/ferias.py (30 min)
9. Adicionar decorators (10 min)
10. requirements.txt (2 min)

**Total:** ~106 minutos (1h46min)

---

## 🎯 Teste de Smoke (Verificação Básica)

```python
# Script para testar se app inicia
import os
os.environ['SECRET_KEY'] = 'test'
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

from app import create_app
app = create_app()
print("✅ App criado com sucesso")

with app.app_context():
    from extensions import db
    db.create_all()
    print("✅ Database inicializado")
    
    from models import User, Empresa
    e = Empresa(razao_social="Test", cnpj="12345678000190", endereco="Rua X")
    db.session.add(e)
    db.session.commit()
    print("✅ Model funcionando")

print("\n🎉 Todos os testes básicos passaram!")
```

---

## 📞 Suporte para Dúvidas

**Se encontrar dúvida sobre:**

| Dúvida | Referência |
|--------|-----------|
| Credenciais | GUIA_CORRECOES_ESPECIFICAS.md #1-3 |
| Atributos | Tabela de referência acima |
| Imports | GUIA_CORRECOES_ESPECIFICAS.md #9 |
| Segurança | ANALISE_COMPLETA_PROJETO.md - Problemas Segurança |
| Banco de Dados | ANALISE_COMPLETA_PROJETO.md - Issues BD |
| Decorators | GUIA_CORRECOES_ESPECIFICAS.md #3 |

---

**Última Atualização:** 2026-06-12  
**Status:** ✅ Análise Completa  
**Próximo Passo:** Iniciar correções Fase 1
