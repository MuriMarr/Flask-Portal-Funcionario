from flask import render_template, request, send_file
from datetime import datetime
from io import BytesIO
from models import User, Marcacao, Ferias
from app import db
from routes.common.pdf_utils import gerar_pdf
from . import relatorios_bp

# =============================
# RELATÓRIO FINANCEIRO MENSAL
# =============================
@relatorios_bp.route('/admin/relatorios/financeiro', methods=['GET'])
def relatorio_financeiro():
    mes = request.args.get('mes', datetime.now().month)
    ano = request.args.get('ano', datetime.now().year)

    funcionarios = User.query.filter_by(tipo='funcionario').all()
    dados = []

    for f in funcionarios:
        marcacoes = Marcacao.query.filter(
            db.extract('month', Marcacao.data) == mes,
            db.extract('year', Marcacao.data) == ano,
            Marcacao.user_id == f.id
        ).all()

        horas_trabalhadas = sum([m.total_horas for m in marcacoes if m.total_horas], 0)
        horas_extras = sum([m.extras for m in marcacoes if m.extras], 0)

        salario_base = f.salario or 0
        valor_hora = salario_base / 220
        valor_extras = horas_extras * (valor_hora * 1.5)
        bruto = salario_base + valor_extras
        descontos = bruto * 0.09  # Exemplo simplificado (INSS)
        liquido = bruto - descontos

        dados.append({
            "funcionario": f.nome,
            "cargo": f.cargo or "-",
            "salario_base": salario_base,
            "horas_trabalhadas": horas_trabalhadas,
            "horas_extras": horas_extras,
            "valor_extras": valor_extras,
            "bruto": bruto,
            "descontos": descontos,
            "liquido": liquido
        })

    if 'pdf' in request.args:
        pdf_bytes = gerar_pdf("relatorios/relatorio_financeiro_pdf.html", dados=dados, mes=mes, ano=ano)
        return send_file(BytesIO(pdf_bytes), download_name=f"relatorio_financeiro_{mes}_{ano}.pdf", as_attachment=True)

    return render_template("relatorios/relatorio_financeiro_pdf.html", dados=dados, mes=mes, ano=ano)

# =============================
# RELATÓRIO DE FÉRIAS / AFASTAMENTOS
# =============================
@relatorios_bp.route('/admin/relatorios/ferias', methods=['GET'])
def relatorio_ferias():
    ferias = Ferias.query.order_by(Ferias.data_inicio.desc()).all()

    if 'pdf' in request.args:
        pdf_bytes = gerar_pdf("relatorios/relatorio_ferias_pdf.html", ferias=ferias)
        return send_file(BytesIO(pdf_bytes), download_name="relatorio_ferias.pdf", as_attachment=True)

    return render_template("relatorios/relatorio_ferias_pdf.html", ferias=ferias)

# =============================
# RELATÓRIO DE JORNADA (com filtro)
# =============================
@relatorios_bp.route('/admin/relatorios/jornada', methods=['GET'])
def relatorio_jornada_financeiro():
    data_inicio = request.args.get('inicio')
    data_fim = request.args.get('fim')

    query = Marcacao.query
    if data_inicio and data_fim:
        query = query.filter(Marcacao.data.between(data_inicio, data_fim))

    registros = query.order_by(Marcacao.data.desc()).all()

    if 'pdf' in request.args:
        pdf_bytes = gerar_pdf("relatorios/relatorio_jornada_pdf.html", registros=registros)
        return send_file(BytesIO(pdf_bytes), download_name="relatorio_jornada.pdf", as_attachment=True)

    return render_template("relatorios/relatorio_jornada_pdf.html", registros=registros)