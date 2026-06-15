from flask import Blueprint

from routes.superadmin import superadmin_bp
from routes.admin import admin_bp
from routes.funcionarios import funcionarios_bp
from routes.avisos import avisos_bp
from routes.documentos import documentos_bp

__all__ = ["admin_bp", "funcionarios_bp", "superadmin_bp", "avisos_bp", "documentos_bp"]