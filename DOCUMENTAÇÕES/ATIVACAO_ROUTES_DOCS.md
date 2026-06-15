# Rota de Ativação de Superadmin - Documentação

## Visão Geral
A rota de ativação do superadmin permite gerenciar superadministradores do sistema com integração completa ao banco de dados, criação de avisos, e logs de ações.

## Rotas Implementadas

### 1. **GET/POST** `/superadmin/ativacoes` - Listar Ativações
- **Descrição**: Lista todos os superadmins cadastrados no sistema
- **Proteção**: Requer autenticação e permissão de superadmin
- **Template**: `listar_ativacoes.html`
- **Funcionalidades**:
  - Visualizar todos os superadmins com status (Ativo/Inativo)
  - Acesso rápido às ações de editar, desativar/reativar e excluir
  - Botão para criar novo superadmin

### 2. **GET/POST** `/superadmin/ativacoes/novo` - Novo Superadmin
- **Descrição**: Cria um novo superadmin através do painel de controle
- **Proteção**: Requer autenticação e permissão de superadmin
- **Template**: `nova_ativacao.html`
- **Campos**:
  - Nome (obrigatório)
  - Email (obrigatório, único)
  - Senha (obrigatório, mínimo 6 caracteres)
  - Telefone (opcional)
  - Empresa (obrigatório)
- **Validações**:
  - Verifica se o email já existe no sistema
  - Verifica se a empresa já possui um superadmin ativo
  - Confirma a existência da empresa
- **Ações ao sucesso**:
  - Cria novo usuário com tipo "superadmin"
  - Criação automática de aviso no sistema
  - Redirecionamento para lista de ativações

### 3. **GET/POST** `/superadmin/ativacoes/<id>/editar` - Editar Superadmin
- **Descrição**: Edita informações de um superadmin existente
- **Proteção**: Requer autenticação e permissão de superadmin
- **Template**: `editar_ativacao.html`
- **Campos Editáveis**:
  - Nome, Email, Telefone
  - Data de Nascimento
  - Nova Senha (opcional)
  - Endereço (Rua, Número, Complemento, Bairro, Cidade, UF)
- **Ações ao sucesso**:
  - Atualização dos dados no banco
  - Criação de aviso de atualização
  - Redirecionamento para lista de ativações

### 4. **POST** `/superadmin/ativacoes/<id>/desativar` - Desativar Superadmin
- **Descrição**: Desativa um superadmin ativo
- **Proteção**: Requer autenticação e permissão de superadmin
- **Ações ao sucesso**:
  - Define `ativo = False` no banco de dados
  - Criação de aviso de desativação
  - Redirecionamento para lista de ativações

### 5. **POST** `/superadmin/ativacoes/<id>/reativar` - Reativar Superadmin
- **Descrição**: Reativa um superadmin inativo
- **Proteção**: Requer autenticação e permissão de superadmin
- **Validações**:
  - Verifica se a empresa já possui outro superadmin ativo
- **Ações ao sucesso**:
  - Define `ativo = True` no banco de dados
  - Criação de aviso de reativação
  - Redirecionamento para lista de ativações

### 6. **POST** `/superadmin/ativacoes/<id>/excluir` - Excluir Superadmin
- **Descrição**: Remove um superadmin do sistema
- **Proteção**: Requer autenticação e permissão de superadmin
- **Aviso**: Ação irreversível
- **Ações ao sucesso**:
  - Deletar usuário do banco de dados
  - Criação de aviso de exclusão
  - Redirecionamento para lista de ativações

## Padrões Implementados

### 1. **Banco de Dados**
- Uso de SQLAlchemy com `db.session`
- Relacionamentos com tabela `Empresa`
- Herança do modelo `User` com tipo "superadmin"

### 2. **Avisos**
- Criação automática de avisos para cada ação importante
- Registros com timestamp (data e hora)
- Integração com a tabela `Aviso`

### 3. **Segurança**
- Decorador `@superadmin_required` para proteção de rotas
- Decorador `@login_required` para autenticação
- Validação de dados de entrada
- Verificação de duplicatas (email)
- Hashing de senhas com `set_senha()`

### 4. **Flash Messages**
- Mensagens de sucesso/erro para feedback do usuário
- Classes: "success", "danger", "warning", "info"

### 5. **Templates**
- Herança do `base.html`
- Responsivo com Bootstrap
- Confirmação de exclusão via JavaScript
- Cards para organização de informações

## Fluxo de Uso

1. Superadmin entra em `/superadmin/ativacoes`
2. Clica em "+ Novo Superadmin"
3. Preenche formulário com dados necessários
4. Sistema cria novo superadmin e aviso
5. Superadmin pode editar, desativar, reativar ou excluir conforme necessário

## Notas Importantes

- Um superadmin pode ter apenas uma empresa associada
- Só pode haver um superadmin ativo por empresa
- Todas as ações geram avisos automáticos no sistema
- As senhas são armazenadas com hash (seguro)
- O campo CPF é preenchido com valor padrão "000.000.000-00" (pode ser ajustado)
