from flask import Blueprint

documentos_bp = Blueprint("documentos", __name__, url_prefix="/documentos", template_folder="documentos")

from . import documentos