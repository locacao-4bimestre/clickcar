from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

tabela_favoritos = db.Table('tabela_favoritos',
    db.Column('user_id', db.Integer, db.ForeignKey('usuarios.id'), primary_key=True),
    db.Column('veiculo_id', db.Integer, db.ForeignKey('veiculos.id'), primary_key=True)
)

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

    perfil_id = db.Column(db.Integer, db.ForeignKey(
        'perfis.id'), nullable=False)
    telefone = db.Column(db.String(20))
    cpf = db.Column(db.String(20))
   
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    email_verificado = db.Column(db.Boolean, default=False)
    codigo_verificacao = db.Column(db.String(6))
    cnh = db.Column(db.String(11), unique=True)
    lista_favoritos = db.relationship('Veiculo', secondary=tabela_favoritos, 
                                      backref=db.backref('favoritado_por', lazy='dynamic'))

    enderecos = db.relationship(
        "Endereco",
        backref="usuario",
        cascade="all, delete-orphan",
        lazy=True
    )

    tokens = db.relationship('Token', backref='usuarios',
                             lazy=True, cascade="all, delete-orphan")
    reservas = db.relationship(
        'Reserva',
        backref='usuario',
        cascade="all, delete-orphan"
    )

    def get_id(self):
        return str(self.id)


class Endereco(db.Model):
    __tablename__ = 'enderecos'

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('usuarios.id'),
        nullable=False
    )

    estado = db.Column(db.String(2), nullable=False)  # Ex: SP, RJ
    cidade = db.Column(db.String(100), nullable=False)
    bairro = db.Column(db.String(120), nullable=False)
    logradouro = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(20), nullable=False)
    complemento = db.Column(db.String(150), nullable=True)
    cep = db.Column(db.String(9), nullable=False)  # Formato 00000-000

   

class TipoVeiculo(db.Model):
    __tablename__ = 'tipo_veiculo'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.Text)

    veiculos = db.relationship('Veiculo', backref='tipo', lazy=True)


class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(2000), nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey(
        'usuarios.id', ondelete="CASCADE"), nullable=False)


class Veiculo(db.Model):
    __tablename__ = 'veiculos'
    id = db.Column(db.Integer, primary_key=True)
    modelo = db.Column(db.String(120), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    placa = db.Column(db.String(20), unique=True)
    cor = db.Column(db.String(30))
    tipo_id = db.Column(db.Integer, db.ForeignKey(
        'tipo_veiculo.id'), nullable=False)
    preco_por_dia = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default='disponivel')
    localizacao = db.Column(db.String(150))
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)


class Reserva(db.Model):
    __tablename__ = 'reservas'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(
        'usuarios.id'), nullable=False)
    veiculo_id = db.Column(db.Integer, db.ForeignKey(
        'veiculos.id'), nullable=False)
    data_inicio = db.Column(db.Date, nullable=False)
    data_fim = db.Column(db.Date, nullable=False)
    # pendente, confirmada, cancelada
    status = db.Column(db.String(30), default='pendente')
    valor_total = db.Column(db.Float)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)

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
    veiculo_id = db.Column(db.Integer, db.ForeignKey(
        'veiculos.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)

    veiculo = db.relationship("Veiculo", backref="fotos", lazy=True)


class Newsletter(db.Model):
    __tablename__ = 'newsletter'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    criado_em = db.Column(db.DateTime, default=datetime.utcnow)
