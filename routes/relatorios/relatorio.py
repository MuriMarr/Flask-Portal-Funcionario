from flask import render_template, request, make_response
from datetime import datetime, timedelta
from sqlalchemy import extract
from models import User, Ponto
from utils import calcular_horas_ponto
from routes.common.pdf_utils import gerar_pdf
from flask_login import login_required
from . import relatorios_bp

@relatorios_bp.route("/jornada", methods=["GET"])
@login_required
def relatorio_jornada():
    mes = request.args.get("mes", datetime.now().strftime("%Y-%m"))
    ano, mes = map(int, mes.split("-"))

    funcionarios = User.query.filter_by(tipo="funcionario").all()
    relatorio = []

    for func in funcionarios:
        pontos = (Ponto.query.filter(
            Ponto.user_id == func.id, 
            extract("year", Ponto.data) == ano, 
            extract("month", Ponto.data) == mes).all())
        
        total_trabalhado = timedelta()
        total_extras = timedelta()
        total_deficit = timedelta()

        for p in pontos:
            resultado = calcular_horas_ponto(p, carga=timedelta(hours=8))
            total_trabalhado += resultado["total_trabalhado"]
            total_extras += resultado["extras"]
            total_deficit += resultado["deficit"]

        banco = total_trabalhado + total_extras - total_deficit

        relatorio.append({
            "funcionario": func.nome,
            "total_trabalhado": total_trabalhado,
            "total_extras": total_extras,
            "total_deficit": total_deficit,
            "banco": banco
        })

    return render_template("relatorios/relatorio_jornada.html", relatorio=relatorio, mes=f"{ano}-{mes:02d}")

@relatorios_bp.route("/jornada/pdf")
@login_required
def relatorio_jornada_pdf():
    mes = request.args.get("mes", datetime.now().strftime("%Y-%m"))
    ano, mes = map(int, mes.split("-"))

    funcionarios = User.query.filter_by(tipo="funcionario").all()
    relatorio = []

    for func in funcionarios:
        pontos = (Ponto.query.filter(
            Ponto.user_id == func.id, 
            extract("year", Ponto.data) == ano, 
            extract("month", Ponto.data) == mes).all())

        total_trabalhado = timedelta()
        total_extras = timedelta()
        total_deficit = timedelta()

        for p in pontos:
            resultado = calcular_horas_ponto(p, carga=timedelta(hours=8))
            total_trabalhado += resultado["total_trabalhado"]
            total_extras += resultado["extras"]
            total_deficit += resultado["deficit"]

        banco = total_trabalhado + total_extras - total_deficit

        relatorio.append({
            "funcionario": func.nome,
            "total_trabalhado": total_trabalhado,
            "total_extras": total_extras,
            "total_deficit": total_deficit,
            "banco": banco
        })

    pdf = gerar_pdf("relatorios/relatorio_jornada_pdf.html", relatorio=relatorio, mes=f"{ano}-{mes:02d}")

    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=relatorio_jornada_{ano}_{mes:02d}.pdf'
    return response