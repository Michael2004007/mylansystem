import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

from blueprints.auth import auth_bp
from blueprints.inicio import inicio_bp
from blueprints.tareas import tareas_bp
from blueprints.campanas import campanas_bp
from blueprints.influencers import influencers_bp
from blueprints.ecommerce import ecommerce_bp
from blueprints.calendario import calendario_bp
from blueprints.reportes import reportes_bp
from blueprints.usuarios import usuarios_bp
from blueprints.ideas_campanas import ideas_campanas_bp

from dao.usuario_dao import UsuarioDAO
from dao.permiso_dao import PermisoDAO
from dao.configuracion_dao import ConfiguracionDAO
from dao.db_bootstrap import bootstrap_schema

load_dotenv()


def create_app():
    app = Flask(__name__)

    app.secret_key = os.environ.get('SECRET_KEY', 'mylan_secret_2025_fallback_only_for_dev')
    CSRFProtect(app)

    os.makedirs('static/uploads', exist_ok=True)
    app.config['UPLOAD_FOLDER'] = 'static/uploads'
    app.config['MAX_CONTENT_LENGTH'] = 52428800  # 50MB

    if os.environ.get('BOOTSTRAP_SCHEMA', '1') == '1':
        bootstrap_schema()

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Inicia sesion para continuar.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return UsuarioDAO.obtener(int(user_id))

    @app.context_processor
    def inject_permisos():
        def tiene_permiso(modulo):
            if not current_user.is_authenticated:
                return False
            if current_user.es_admin():
                return True
            return PermisoDAO.tiene_permiso(current_user.id, modulo)

        return dict(tiene_permiso=tiene_permiso)

    @app.context_processor
    def inject_logo():
        logo_ruta = ConfiguracionDAO.obtener_logo()
        return dict(logo_ruta=logo_ruta)

    app.register_blueprint(auth_bp)
    app.register_blueprint(inicio_bp, url_prefix='/inicio')
    app.register_blueprint(tareas_bp, url_prefix='/tareas')
    app.register_blueprint(campanas_bp, url_prefix='/campanas')
    app.register_blueprint(influencers_bp, url_prefix='/influencers')
    app.register_blueprint(ecommerce_bp, url_prefix='/ecommerce')
    app.register_blueprint(calendario_bp, url_prefix='/calendario')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(ideas_campanas_bp, url_prefix='/ideas-campanas')

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('inicio.index'))
        return redirect(url_for('auth.login'))

    return app


app = create_app()


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV', 'production') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
