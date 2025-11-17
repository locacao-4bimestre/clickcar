from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class Perfil(db.Model):
    __tablename__ = 'perfis'
    id = db.Column(db.Integer, primary_key=True)
    nome_perfil = db.Column(db.String(50), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', backref='perfil', lazy=True)

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(200), nullable=False)
    perfil_id = db.Column(db.Integer, db.ForeignKey('perfis.id'), nullable=False)
    telefone = db.Column(db.String(20))      
    cpf = db.Column(db.String(20))          
    endereco = db.Column(db.String(255))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    email_verificado = db.Column(db.Boolean, default=False)
    codigo_verificacao = db.Column(db.String(6))



    def get_id(self):
        return str(self.id)

class TipoVeiculo(db.Model):
    __tablename__ = 'tipo_veiculo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text)

    veiculos = db.relationship('Veiculo', backref='tipo', lazy=True)

class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    placa = db.Column(db.String(20), unique=True)
    cor = db.Column(db.String(30))
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_veiculo.id'), nullable=False)
    preco_por_dia = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='disponivel')
    localizacao = db.Column(db.String(150))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(30), default='pendente')  # pendente, confirmada, cancelada
    valor_total = db.Column(db.Float)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref='reservas')
    veiculo = db.relationship('Veiculo', backref='reservas')

class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)

    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    endereco = db.Column(db.String(200))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

class VehiclePhoto(db.Model):
    __tablename__ = 'vehicle_photos'

    id = db.Column(db.Integer, primary_key=True)
    veiculo_id = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)

    veiculo = db.relationship("Veiculo", backref="fotos", lazy=True)
