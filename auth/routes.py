from datetime import datetime, date, timezone
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models import User
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        senha = request.form.get("senha", "").strip()

        if not email or not senha:
            flash("Email e senha são obrigatórios.", "warning")
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
            flash("Usuário desconhecido. Contate o suporte.", "danger")

        return render_template("login.html")

    return render_template("login.html")

@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    if request.method == "POST":
        return ("", 204)
    flash("Logout realizado com sucesso.", "success")
    return redirect(url_for("auth.login"))

@auth_bp.route("/logout_beacon", methods=['POST'])
def logout_beacon():
    try:
        logout_user()
    except Exception:
        pass
    session.clear()
    return ('', 204)

@auth_bp.route("/refresh_session", methods=['POST'])
@login_required
def refresh_session():
    """Endpoint para renovar a sessão do usuário (heartbeat)"""
    session.permanent = True
    session.modified = True
    return jsonify({'status': 'ok', 'user_id': current_user.id}), 200

@auth_bp.route('/registrar_funcionario', methods=['GET', 'POST'])
def registrar_funcionario():
    if request.method == 'POST':
        nome = request.form.get('nome', '').strip()
        data_nascimento = request.form.get('data_nascimento', '').strip()
        email = request.form.get('email', '').strip().lower()
        senha = request.form.get('senha', '')
        cpf = request.form.get('cpf', '').strip()
        cargo = request.form.get('cargo', '').strip()
        try:
            salario_mensal = float(request.form.get('salario_mensal', 0) or 0)
        except ValueError:
            salario_mensal = 1940.00
        telefone = request.form.get('telefone', '').strip()
        rua = request.form.get('rua', '').strip()
        numero = request.form.get('numero', '').strip()
        bairro = request.form.get('bairro', '').strip()
        complemento = request.form.get('complemento', '').strip()
        cidade_uf = request.form.get('cidade_uf', '').strip()
        tipo = request.form.get('tipo', 'funcionario')
        data_admissao = request.form.get('data_admissao', '').strip()
        ativo = True

        if not nome or not email or not senha or not data_nascimento:
            flash('Preencha todos os campos obrigatórios!', 'warning')
            return redirect(url_for('auth.registrar_funcionario'))
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado.', 'warning')
            return redirect(url_for('auth.registrar_funcionario'))

        try:
            data_nascimento_parsed = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Data de nascimento inválida.', 'warning')
            return redirect(url_for('auth.registrar_funcionario'))

        if data_admissao:
            try:
                data_admissao_parsed = datetime.strptime(data_admissao, '%Y-%m-%d').date()
            except ValueError:
                flash('Data de admissão inválida.', 'warning')
                return redirect(url_for('auth.registrar_funcionario'))
        else:
            data_admissao_parsed = date.today()
        
        novo_user = User(
            nome=nome,
            data_nascimento=data_nascimento_parsed,
            cpf=cpf,
            cargo=cargo,
            salario_mensal=salario_mensal,
            email=email,
            senha=generate_password_hash(senha),
            tipo=tipo,
            rua=rua,
            telefone=telefone,
            cidade_uf=cidade_uf,
            complemento=complemento,
            bairro=bairro,
            numero=numero,
            data_admissao=data_admissao_parsed,
            ativo=ativo) 
        
        db.session.add(novo_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso. Faça login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')