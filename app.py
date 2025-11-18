from controllers.controller import main
from flask import Flask
from config import Config
from models.models import db, Perfil, Usuario
from flask_migrate import Migrate
from flask_login import LoginManager
from werkzeug.security import generate_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# UPLOADS
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
