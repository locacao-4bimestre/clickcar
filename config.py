import os

from sqlalchemy import create_engine
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get(
        'SECRET_KEY') or 'troca-essa-chave-por-uma-secreta'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'locacao.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
