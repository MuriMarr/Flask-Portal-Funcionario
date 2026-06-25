import os
from datetime import datetime
from flask_login import current_user
from flask import Flask, flash, redirect, render_template, url_for, session
from config import Config
from extensions import db, migrate, login_manager
from models import User
from dotenv import load_dotenv, find_dotenv
from utils import format_timedelta

load_dotenv(find_dotenv(usecwd=True))
CHAVE_SECRETA_ADMIN = os.environ.get('CHAVE_SECRETA_ADMIN')

if not CHAVE_SECRETA_ADMIN:
    raise ValueError(
        "CHAVE_SECRETA_ADMIN não configurada. Configure no arquivo .env"
    )

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        flash('Acesso negado', 'danger')
        return redirect(url_for('funcionarios.dashboard'))
    
    app.jinja_env.filters['format_timedelta'] = format_timedelta

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    @app.before_request
    def refresh_permanent_session():
        try:
            if current_user and current_user.is_authenticated:
                session.permanent = True
                session.modified = True
        except Exception:
            pass

    # Blueprints
    from routes.admin import admin_bp
    from routes.relatorios import relatorios_bp
    from routes.avisos import avisos_bp
    from routes.documentos import documentos_bp
    from routes.funcionarios import funcionarios_bp
    from routes.superadmin import superadmin_bp
    from routes.empresas import empresas_bp
    from auth import auth_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(relatorios_bp, url_prefix='/relatorios')
    app.register_blueprint(avisos_bp, url_prefix='/avisos')
    app.register_blueprint(documentos_bp, url_prefix='/documentos')
    app.register_blueprint(funcionarios_bp, url_prefix='/funcionarios')
    app.register_blueprint(superadmin_bp, url_prefix='/superadmin')
    app.register_blueprint(empresas_bp, url_prefix='/empresas')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    @app.route("/")
    def index():
        if not current_user or not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        if current_user.tipo == 'superadmin':
            return redirect(url_for('superadmin.dashboard'))
        if current_user.tipo == 'admin':
            return redirect(url_for('admin.dashboard'))
        
        # Padrão: funcionário
        return redirect(url_for('funcionarios.dashboard'))
    
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}
    
    return app

@login_manager.user_loader
def carregar_usuario(user_id):
    try:
        return User.query.get(int(user_id))
    except (ValueError, TypeError):
        return None

# Rodar o app
if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)