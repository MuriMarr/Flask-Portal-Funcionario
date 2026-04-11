from flask import render_template, request, redirect, url_for, flash, current_app as app
from flask_login import login_required
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from models import User, Empresa, Aviso
from extensions import db
from utils import superadmin_required, log_action
from . import superadmin_bp


@superadmin_bp.route("/ativacoes", methods=["GET"])
@login_required
@superadmin_required
def listar_ativacoes():
    """Lista todos os superadmins cadastrados no sistema"""
    superadmins = User.query.filter_by(tipo="superadmin").all()
    empresas = Empresa.query.all()
    return render_template("superadmin/listar_ativacoes.html", superadmins=superadmins, empresas=empresas)


@superadmin_bp.route("/ativacoes/novo", methods=["GET", "POST"])
@login_required
@superadmin_required
def nova_ativacao():
    """Cria um novo superadmin através do painel do superadmin"""
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        telefone = request.form.get("telefone")
        empresa_id = request.form.get("empresa_id", type=int)

        # Validações
        if not nome or not email or not senha or not empresa_id:
            flash("Preencha todos os dados obrigatórios.", "danger")
            return redirect(url_for("superadmin.nova_ativacao"))

        # Verifica se o email já existe
        if User.query.filter_by(email=email).first():
            flash("Já existe um usuário com este email.", "danger")
            return redirect(url_for("superadmin.nova_ativacao"))

        # Verifica se a empresa existe
        empresa = Empresa.query.get_or_404(empresa_id)

        # Verifica se a empresa já possui um superadmin ativo
        superadmin_existente = User.query.filter_by(
            empresa_id=empresa_id, tipo="superadmin", ativo=True
        ).first()
        if superadmin_existente:
            flash(f"A empresa {empresa.razao_social} já possui um superadmin ativo.", "warning")
            return redirect(url_for("superadmin.nova_ativacao"))

        # Cria novo superadmin
        novo_superadmin = User(
            nome=nome,
            email=email,
            telefone=telefone,
            tipo="superadmin",
            empresa_id=empresa_id,
            ativo=True,
            cpf="000.000.000-00",  # Pode ser ajustado conforme necessário
            salario_mensal=0.0,
        )
        novo_superadmin.set_senha(senha)
        db.session.add(novo_superadmin)
        db.session.commit()

        # Log da ação
        log_action(request.environ.get("REMOTE_USER", "sistema"), f"Novo superadmin criado: {nome} para {empresa.razao_social}")

        # Cria aviso notificando a ativação
        aviso = Aviso(
            titulo=f"Novo Superadmin Ativado",
            conteudo=f"Um novo superadmin ({nome}) foi ativado para a empresa {empresa.razao_social} em {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}.",
        )
        db.session.add(aviso)
        db.session.commit()

        flash(f"Superadmin '{nome}' criado com sucesso para {empresa.razao_social}!", "success")
        return redirect(url_for("superadmin.listar_ativacoes"))

    empresas = Empresa.query.all()
    return render_template("superadmin/nova_ativacao.html", empresas=empresas)


@superadmin_bp.route("/ativacoes/<int:id>/editar", methods=["GET", "POST"])
@login_required
@superadmin_required
def editar_ativacao(id):
    """Edita informações de um superadmin"""
    superadmin = User.query.get_or_404(id)

    if superadmin.tipo != "superadmin":
        flash("Este usuário não é um superadmin.", "danger")
        return redirect(url_for("superadmin.listar_ativacoes"))

    if request.method == "POST":
        superadmin.nome = request.form.get("nome")
        superadmin.email = request.form.get("email")
        superadmin.telefone = request.form.get("telefone")

        # Se houver nova senha
        nova_senha = request.form.get("nova_senha")
        if nova_senha:
            superadmin.set_senha(nova_senha)

        # Dados endereço (opcional)
        superadmin.rua = request.form.get("rua")
        superadmin.numero = request.form.get("numero")
        superadmin.complemento = request.form.get("complemento")
        superadmin.bairro = request.form.get("bairro")
        superadmin.cidade = request.form.get("cidade")
        superadmin.uf = request.form.get("uf")
        superadmin.data_nascimento = request.form.get("data_nascimento") or None

        db.session.commit()

        # Cria aviso notificando a edição
        aviso = Aviso(
            titulo="Superadmin Atualizado",
            conteudo=f"As informações do superadmin {superadmin.nome} foram atualizadas em {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}.",
        )
        db.session.add(aviso)
        db.session.commit()

        flash(f"Superadmin '{superadmin.nome}' atualizado com sucesso!", "success")
        return redirect(url_for("superadmin.listar_ativacoes"))

    return render_template("superadmin/editar_ativacao.html", superadmin=superadmin)


@superadmin_bp.route("/ativacoes/<int:id>/desativar", methods=["POST"])
@login_required
@superadmin_required
def desativar_superadmin(id):
    """Desativa um superadmin"""
    superadmin = User.query.get_or_404(id)

    if superadmin.tipo != "superadmin":
        flash("Este usuário não é um superadmin.", "danger")
        return redirect(url_for("superadmin.listar_ativacoes"))

    superadmin.ativo = False
    db.session.commit()

    # Cria aviso notificando a desativação
    aviso = Aviso(
        titulo="Superadmin Desativado",
        conteudo=f"O superadmin {superadmin.nome} foi desativado em {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}.",
    )
    db.session.add(aviso)
    db.session.commit()

    flash(f"Superadmin '{superadmin.nome}' desativado com sucesso!", "success")
    return redirect(url_for("superadmin.listar_ativacoes"))


@superadmin_bp.route("/ativacoes/<int:id>/reativar", methods=["POST"])
@login_required
@superadmin_required
def reativar_superadmin(id):
    """Reativa um superadmin"""
    superadmin = User.query.get_or_404(id)

    if superadmin.tipo != "superadmin":
        flash("Este usuário não é um superadmin.", "danger")
        return redirect(url_for("superadmin.listar_ativacoes"))

    # Verifica se a empresa já possui outro superadmin ativo
    outro_superadmin = User.query.filter(
        User.empresa_id == superadmin.empresa_id,
        User.tipo == "superadmin",
        User.ativo == True,
        User.id != id
    ).first()

    if outro_superadmin:
        flash(
            f"A empresa já possui um superadmin ativo ({outro_superadmin.nome}). Desative-o primeiro.",
            "warning"
        )
        return redirect(url_for("superadmin.listar_ativacoes"))

    superadmin.ativo = True
    db.session.commit()

    # Cria aviso notificando a reativação
    aviso = Aviso(
        titulo="Superadmin Reativado",
        conteudo=f"O superadmin {superadmin.nome} foi reativado em {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}.",
    )
    db.session.add(aviso)
    db.session.commit()

    flash(f"Superadmin '{superadmin.nome}' reativado com sucesso!", "success")
    return redirect(url_for("superadmin.listar_ativacoes"))


@superadmin_bp.route("/ativacoes/<int:id>/excluir", methods=["POST"])
@login_required
@superadmin_required
def excluir_superadmin(id):
    """Exclui um superadmin do sistema"""
    superadmin = User.query.get_or_404(id)

    if superadmin.tipo != "superadmin":
        flash("Este usuário não é um superadmin.", "danger")
        return redirect(url_for("superadmin.listar_ativacoes"))

    nome = superadmin.nome
    empresa = superadmin.empresa

    db.session.delete(superadmin)
    db.session.commit()

    # Cria aviso notificando a exclusão
    aviso = Aviso(
        titulo="Superadmin Excluído",
        conteudo=f"O superadmin {nome} foi excluído do sistema em {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}. Empresa: {empresa.razao_social if empresa else 'N/A'}",
    )
    db.session.add(aviso)
    db.session.commit()

    flash(f"Superadmin '{nome}' excluído com sucesso!", "success")
    return redirect(url_for("superadmin.listar_ativacoes"))
