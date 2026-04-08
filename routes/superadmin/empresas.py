from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Empresa, User
from extensions import db
from utils import superadmin_required, validar_cnpj
from datetime import datetime, timezone
from . import superadmin_bp

@superadmin_bp.route("/empresas/novo", methods=["GET", "POST"])
@login_required
@superadmin_required
def nova_empresa():
    if request.method == "POST":
        dados = request.form
        razao_social = dados.get("razao_social")
        cnpj = ''.join(filter(str.isdigit, dados.get("cnpj", "")))
        endereco = dados.get("endereco")
        telefone = dados.get("telefone")
        inscricao_estadual = dados.get("inscricao_estadual")
        email = dados.get("email")
        carga_mensal = dados.get("carga_mensal", type=int) or 220

        if not razao_social or not cnpj or not endereco:
            flash("Nome, CNPJ e endereço são obrigatórios.", "danger")
            return redirect(url_for("superadmin.nova_empresa"))
        
        if not validar_cnpj(cnpj):
            flash("CNPJ inválido. Digite exatamente 14 números.", "danger")
            return redirect(url_for("superadmin.nova_empresa"))

        empresa = Empresa(
            razao_social=razao_social,
            cnpj=cnpj,
            endereco=endereco,
            telefone=telefone,
            inscricao_estadual=inscricao_estadual,
            email=email,
            carga_mensal=carga_mensal,
            data_cadastro=datetime.now(timezone.utc)
        )
        db.session.add(empresa)
        db.session.commit()
        flash("Empresa criada com sucesso!", "success")
        return redirect(url_for("superadmin.dashboard"))

    return render_template("superadmin/nova_empresa.html")

# EDITAR EMPRESA
@superadmin_bp.route("/empresas/<int:id>/editar", methods=["GET", "POST"])
@login_required
@superadmin_required
def editar_empresa(id):
    empresa = Empresa.query.get_or_404(id)

    if request.method == "POST":
        empresa = Empresa(
            razao_social=request.form.get("razao_social"),
            nome_fantasia=request.form.get("nome_fantasia"),
            cnpj=request.form.get("cnpj"),
            inscricao_estadual=request.form["inscricao_estadual"],
            endereco=request.form.get("endereco"),
            numero=request.form.get("numero"),
            bairro=request.form.get("bairro"),
            cidade=request.form.get("cidade"),
            uf=request.form.get("uf"),
            cep=request.form.get("cep"),
            telefone=request.form.get("telefone"),
            email=request.form.get("email"),
            carga_mensal=request.form.get("carga_mensal", type=int) or empresa.carga_mensal
        )

        db.session.commit()
        flash("Empresa atualizada com sucesso!", "success")
        return redirect(url_for("superadmin.dashboard"))

    return render_template("superadmin/editar_empresa.html", empresa=empresa)

# EXCLUIR EMPRESA
@superadmin_bp.route("/empresas/<int:id>/excluir", methods=["POST"])
@login_required
@superadmin_required
def excluir_empresa(id):
    empresa = Empresa.query.get_or_404(id)
    db.session.delete(empresa)
    db.session.commit()
    flash("Empresa excluída com sucesso!", "success")
    return redirect(url_for("superadmin.dashboard"))

@superadmin_bp.route("/empresas/<int:id>/definir_admin", methods=["GET", "POST"])
@login_required
@superadmin_required
def definir_admin(id):
    empresa = Empresa.query.get_or_404(id)

    if request.method == "POST":
        admin_id = request.form.get("admin_id", type=int)
        if admin_id:
            admin = User.query.get(admin_id)
            if admin and admin.empresa_id == empresa.id:
                empresa.admin_id = admin.id
                admin.tipo = "admin"
                db.session.commit()
                flash(f"{admin.nome} agora é o admin da empresa {empresa.razao_social}", "success")
                return redirect(url_for("superadmin.dashboard"))
            else:
                flash("Admin inválido ou não pertence a esta empresa.", "danger")
    
    funcionarios = User.query.filter_by(empresa_id=empresa.id).all()
    return render_template("superadmin/definir_admin.html", empresa=empresa, funcionarios=funcionarios)

@superadmin_bp.route("/empresas")
@login_required
@superadmin_required
def listar_empresas():
    empresas = Empresa.query.all()
    return render_template("superadmin/listar_empresas.html", empresas=empresas)

@superadmin_bp.route('/primeiro-cadastro', methods=['GET', 'POST'])
def primeiro_cadastro_empresa():
    if request.method == 'POST':
        empresa = Empresa(
            razao_social=request.form['razao_social'],
            nome_fantasia=request.form.get('nome_fantasia'),
            cnpj=request.form['cnpj'],
            inscricao_estadual=request.form.get('inscricao_estadual'),
            endereco=request.form['endereco'],
            numero=request.form['numero'],
            bairro=request.form['bairro'],
            cidade=request.form['cidade'],
            uf=request.form['uf'],
            cep=request.form['cep'],
            telefone=request.form['telefone'],
            email=request.form['email']
        )
        db.session.add(empresa)
        db.session.commit()
        flash("Empresa cadastrada com sucesso!", "success")
        return redirect(url_for('auth.login'))
    return render_template('superadmin/primeiro_cadastro_empresa.html')