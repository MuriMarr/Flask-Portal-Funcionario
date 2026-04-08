from flask import Blueprint
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

relatorios_bp = Blueprint("relatorios", __name__, url_prefix="/admin/relatorios", template_folder="templates/admin/relatorios")

from . import relatorio, relatorio_financeiro