from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash
from models import Empresa, User, Aviso
from extensions import db
from . import empresas_bp

@empresas_bp.route("/<int:empresa_id>/ativar", methods=["GET", "POST"])
def ativacao(empresa_id):
    """
    Rota de ativação da empresa - Primeiro cadastro de superadmin
    Acessível publicamente para o primeiro login após criação da empresa
    """
    empresa = Empresa.query.get_or_404(empresa_id)

    # Verifica se já existe um superadmin para esta empresa
    superadmin_existente = User.query.filter_by(
        empresa_id=empresa_id, tipo="superadmin", ativo=True
    ).first()
    
    if superadmin_existente:
        flash("Esta empresa já possui um superadmin ativo. Faça login com suas credenciais.", "warning")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        senha = request.form.get("senha")
        telefone = request.form.get("telefone")
        cpf = request.form.get("cpf", "").strip()

        # Validações
        if not nome or not email or not senha or not cpf:
            flash("Preencha todos os dados obrigatórios.", "danger")
            return redirect(url_for("empresas.ativacao", empresa_id=empresa_id))

        # Verifica se o email já existe
        if User.query.filter_by(email=email).first():
            flash("Já existe um usuário com este email no sistema.", "danger")
            return redirect(url_for("empresas.ativacao", empresa_id=empresa_id))

        # Verifica se o CPF já existe
        if User.query.filter_by(cpf=cpf).first():
            flash("Já existe um usuário com este CPF no sistema.", "danger")
            return redirect(url_for("empresas.ativacao", empresa_id=empresa_id))

        # Cria novo superadmin para a empresa
        superadmin = User(
            nome=nome,
            email=email,
            telefone=telefone,
            tipo="superadmin",
            empresa_id=empresa_id,
            ativo=True,
            cpf=cpf,
            salario_mensal=0.0,
        )
        superadmin.set_senha(senha)
        db.session.add(superadmin)
        db.session.commit()

        # Cria aviso de ativação da empresa
        aviso = Aviso(
            titulo=f"Empresa Ativada: {empresa.razao_social}",
            conteudo=f"A empresa {empresa.razao_social} foi ativada no sistema. Superadmin responsável: {nome}. Data: {datetime.now(timezone.utc).strftime('%d/%m/%Y às %H:%M')}.",
        )
        db.session.add(aviso)
        db.session.commit()

        # Faz login automático do superadmin
        login_user(superadmin)

        flash(f"Superadmin '{nome}' criado com sucesso! Bem-vindo ao Portal.", "success")
        return redirect(url_for("superadmin.dashboard"))

    return render_template("empresas/ativacao.html", empresa=empresa)
