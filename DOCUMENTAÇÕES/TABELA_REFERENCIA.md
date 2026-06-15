# 📊 TABELA DE REFERÊNCIA RÁPIDA - ERROS E SOLUÇÕES

## 🔴 CRÍTICOS - Impedem Funcionamento

| # | Arquivo | Linha | Problema | Impacto | Solução |
|---|---------|-------|----------|--------|---------|
| 1 | `config.py` | 6 | Senha PostgreSQL hardcoded | Segurança | Usar .env |
| 2 | `app.py` | 12 | Chave admin hardcoded | Segurança | Usar .env |
| 3 | `models.py` | 58 | `date.today` sem parênteses | Erro ao criar usuário | Mudar para `lambda: date.today()` |
| 4 | `utils.py` | N/A | `calcular_horas_ponto()` não existe | AttributeError | Implementar função |
| 5 | `utils.py` | 28 | Log usa `usuario_id` mas field é `user_id` | Erro DB | Padronizar para `user_id` |
| 6 | `utils.py` | 18 | Decorator sem `@wraps` | Quebra funcionalidade | Adicionar `@wraps(func)` |
| 7 | `models.py` | 18-19 | Backrefs conflitantes | N+1 queries | Renomear backrefs |
| 8 | `app.py` | 70 | `user_loader` sem try/except | Erro 500 | Adicionar validação |
| 9 | `app.py` | 25-27 | `refresh_permanent_session` sem try/except | Erro 500 | Envolver em try/except |
| 10 | `auth/routes.py` | 14-15 | Sem validação em login | SQL injection/XSS | Validar inputs |
| 11 | `app.py` | 12 | SESSION_PERMANENT duplicado | Indefinido | Remover de app.py |
| 12 | `config.py` | 5 | SECRET_KEY fraca | Segurança | Forçar via .env |
| 13 | `admin/dashboard.py` | 11-12 | Não filtra usuários inativos | Dados incorretos | Adicionar `ativo=True` |
| 14 | `admin/dashboard.py` | 21-27 | Lógica de cálculo frágil | Resultado errado | Usar `calcular_horas_ponto()` |
| 15 | `routes/admin/dashboard.py` | 20 | Importa `calcular_horas_ponto` inexistente | ImportError | Implementar em utils.py |
| 16 | `routes/relatorios/relatorio.py` | 23, 62 | Importa função inexistente | ImportError | Implementar em utils.py |
| 17 | Múltiplos | Vários | Sem paginação | Memory overflow | Usar `.paginate()` |
| 18 | `models.py` | 92 | Campo Log referencia `usuario_id` (não existe) | Erro ao usar | Padronizar nomes |

---

## 🟠 ALTOS - Risco de Segurança

| # | Arquivo | Tipo | Problema | Risco | Solução |
|---|---------|------|----------|-------|---------|
| 19 | Múltiplos | Segurança | Sem CSRF protection | XSS/CSRF | pip install Flask-WTF |
| 20 | `auth/routes.py` | Segurança | SQL injection potencial | BD comprometido | Usar ORM (já faz) + validar |
| 21 | `auth/routes.py` | Segurança | Sem rate limiting | Brute force | pip install Flask-Limiter |
| 22 | `models.py` | Validação | Senhas não validadas | Senhas fracas | Adicionar min length |
| 23 | Múltiplos | Audit | Sem audit trail completo | Não sabe quem fez o quê | Log todas ações críticas |
| 24 | `models.py` | BD | Cascade delete perigoso | Perda de dados | Revisar cascades |
| 25 | Múltiplos | API | JSON sem validação | Dados inválidos | Usar schemas (marshmallow) |
| 26 | Múltiplos | Logging | Sem logging de erros | Difícil debug | pip install logging |
| 27 | Múltiplos | Upload | Upload sem validação | Malware/DoS | Validar tipo/tamanho |
| 28 | `app.py` | Erro | Sem error handlers globais | Expõe stack trace | Adicionar @app.errorhandler |
| 29 | Múltiplos | Timezone | Inconsistente | Bugs de data/hora | Usar UTC em todo lugar |
| 30 | `migrations/` | BD | Scripts de migração podem falhar | Inconsistência BD | Revisar e testar |

---

## 🟡 MÉDIOS - Code Smell

| # | Arquivo | Tipo | Problema | Impacto |
|---|---------|------|----------|--------|
| 31 | Múltiplos | Code | Imports desorganizados | Dificuldade manutenção |
| 32 | `relatorios/relatorio.py` | Código | Duplicação (jornada + jornada_pdf) | DRY violation |
| 33 | Múltiplos | Código | Variáveis genéricas (r, p, f) | Legibilidade |
| 34 | Múltiplos | Código | Sem type hints | IDE support ruim |
| 35 | Múltiplos | Docs | Falta docstrings | Difícil entender |
| 36 | `config.py` | Padrão | Não usa herança de configs | Hard manter ambientes |
| 37 | Templates | Código | URLs hardcoded | Refactoring difícil |
| 38 | Raiz | DevOps | Sem .gitignore | .env pode ser commitado |
| 39 | Raiz | DevOps | BD local em produção? | Não está claro |
| 40 | Raiz | Test | Sem testes unitários | Mudanças quebram tudo |
| 41 | `models.py` | BD | Relacionamentos bidirecionais confusos | N+1 queries |
| 42 | Múltiplos | Validação | Sem validação de email | Dados lixo |
| 43 | Templates | Apresentação | Sem formatação de datas | UI inconsistente |
| 44 | Raiz | DevOps | debug=True em produção? | Expõe info |
| 45 | Múltiplos | Segurança | Nem todos endpoints validam permissão | Escalation |

---

## 🟢 BAIXOS - Melhorias

| # | Tipo | Problema |
|---|------|----------|
| 46 | Estilo | Espaçamento inconsistente |
| 47 | Código | Constantes não centralizadas |
| 48 | DevOps | Falta versão em package |
| 49 | DevOps | `db.create_all()` em produção é ruim |
| 50 | BD | Sem índices em tabelas grandes |
| 51 | DevOps | Sem backup/restore strategy |
| 52 | Docs | README vago |
| 53 | Escalab | Sem plano de scale |

---

## ⚡ CHECKLIST DE AÇÃO RÁPIDA

### Hoje (2-3 horas)
- [ ] Criar `.env` com valores seguros
- [ ] Corrigir `config.py` (remover defaults hardcoded)
- [ ] Corrigir `models.py` (data_admissao, relacionamentos)
- [ ] Implementar `calcular_horas_ponto()` em `utils.py`
- [ ] Padronizar `user_id` vs `usuario_id`
- [ ] Testar que app inicia sem ImportError/AttributeError

### Amanhã (4-5 horas)
- [ ] Adicionar validação em login
- [ ] Corrigir admin dashboard (filtro ativo)
- [ ] Adicionar error handlers
- [ ] Testar fluxos principais

### Semana que vem
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Logging
- [ ] Testes unitários

---

## 🔗 Documentos Relacionados

- **ANALISE_ERROS_COMPLETA.md** - Análise detalhada de todos os 53 problemas
- **GUIA_CORRECOES.md** - Código antes/depois com explicações
- Este arquivo - Referência rápida em tabela

---

## 📱 Como Usar

**Para encontrar rápido um erro específico:**

1. Abra `Ctrl+F` neste arquivo
2. Procure por:
   - Número do erro (ex: "19")
   - Nome do arquivo (ex: "config.py")
   - Tipo (ex: "Segurança")

**Para corrigir um erro:**

1. Ache o número na tabela
2. Abra `GUIA_CORRECOES.md`
3. Procure por "CORREÇÃO #N"
4. Siga código antes/depois

---

## 📊 Distribuição de Problemas por Arquivo

```
config.py:           3 críticos
app.py:              5 críticos
models.py:           5 críticos
utils.py:            3 críticos
auth/routes.py:      2 críticos
admin/dashboard.py:  2 críticos
relatorios/:         2 críticos
Múltiplos:           5 críticos
```

---

## 📈 Próximas Etapas

**Fase 1 - Corrigir Críticos (1 dia)**
- Sem este passo, app não funciona direito

**Fase 2 - Segurança (2 dias)**
- Adicionar CSRF, rate limiting, logging
- Validar inputs em todos endpoints

**Fase 3 - Qualidade (3 dias)**
- Type hints, docstrings, testes
- Code review

**Fase 4 - Deploy (1 dia)**
- Setup produção, migrations, backup

