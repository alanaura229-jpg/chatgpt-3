import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Inicia sesión para acceder.'
login_manager.login_message_category = 'warning'


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    # ── Configuración ────────────────────────────────────────────────────────
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-btu-uaslp-2024')

    # MySQL: mysql+pymysql://usuario:contrasena@host:3306/nombre_bd
    # SQLite de respaldo para desarrollo local
    mysql_uri = os.getenv('MYSQL_URI')
    if mysql_uri:
        app.config['SQLALCHEMY_DATABASE_URI'] = mysql_uri
    else:
        basedir = os.path.abspath(os.path.dirname(__file__))
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, '..', 'instance', 'btu.db')}"

    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Subida de CVs
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads', 'cvs')
    app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024   # 5 MB

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # ── Extensiones ───────────────────────────────────────────────────────────
    db.init_app(app)
    login_manager.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes import main
    app.register_blueprint(main)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # ── Crear tablas ──────────────────────────────────────────────────────────
    with app.app_context():
        db.create_all()

    return app
