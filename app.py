import os
from sqlalchemy import create_engine, text
from controllers.controller import main
from flask import Flask
from config import Config
from models.models import db, Perfil, Usuario
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
import cloudinary
import difflib
from itsdangerous import URLSafeTimedSerializer
from extensions import mail
from config import basedir

app = Flask(__name__)
app.config.from_object(Config)

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'clickcarprojeto@gmail.com'
app.config['MAIL_PASSWORD'] = 'eczh aqcw jwfl njga'
app.config['MAIL_DEFAULT_SENDER'] = (
    'ClickCar', 'clickcarprojeto@gmail.com')

serializer = URLSafeTimedSerializer("secret-key-serializer")


# UPLOADS
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

mail.init_app(app)

# EXTENSÕES
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'main.login'


@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


app.register_blueprint(main)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

        if Perfil.query.count() == 0:
            for nome in ["Admin", "Cliente", "Atendimento"]:
                db.session.add(Perfil(nome_perfil=nome))
            db.session.commit()

        if Usuario.query.count() == 0:
            admin_perfil = Perfil.query.filter_by(nome_perfil="Admin").first()

            admin = Usuario(
                nome="Admin",
                email="admin@locadora.com",
                senha_hash=generate_password_hash("admin"),
                perfil_id=admin_perfil.id
            )

            db.session.add(admin)
            db.session.commit()

            print("Admin criado: admin@locadora.com / senha: admin")

    app.run(debug=True)
