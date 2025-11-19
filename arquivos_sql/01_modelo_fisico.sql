/* ============================================================
   Arquivo: 01_modelo_fisico.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Criação do modelo físico (DDL)
   Execução esperada: rodar primeiro, em banco vazio
============================================================ */

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS vehicle_photos;
DROP TABLE IF EXISTS reservas;
DROP TABLE IF EXISTS veiculos;
DROP TABLE IF EXISTS tipo_veiculo;
DROP TABLE IF EXISTS clientes;
DROP TABLE IF EXISTS token;
DROP TABLE IF EXISTS usuarios;
DROP TABLE IF EXISTS perfis;
DROP TABLE IF EXISTS newsletter;

CREATE TABLE perfis (
    id INTEGER PRIMARY KEY,
    nome_perfil TEXT UNIQUE NOT NULL
);

CREATE TABLE usuarios (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha_hash TEXT NOT NULL,
    perfil_id INTEGER NOT NULL,
    telefone TEXT,
    cpf TEXT,
    endereco TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    email_verificado INTEGER DEFAULT 0,
    codigo_verificacao TEXT,
    FOREIGN KEY (perfil_id) REFERENCES perfis(id)
);

CREATE TABLE token (
    id INTEGER PRIMARY KEY,
    token TEXT NOT NULL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    usuario_id INTEGER NOT NULL,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
);

CREATE TABLE tipo_veiculo (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    descricao TEXT
);

CREATE TABLE veiculos (
    id INTEGER PRIMARY KEY,
    modelo TEXT NOT NULL,
    marca TEXT NOT NULL,
    ano INTEGER NOT NULL,
    placa TEXT UNIQUE,
    cor TEXT,
    tipo_id INTEGER NOT NULL,
    preco_por_dia REAL NOT NULL,
    status TEXT DEFAULT 'disponivel',
    localizacao TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tipo_id) REFERENCES tipo_veiculo(id)
);

CREATE TABLE reservas (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    veiculo_id INTEGER NOT NULL,
    data_inicio TEXT NOT NULL,
    data_fim TEXT NOT NULL,
    status TEXT DEFAULT 'pendente',
    valor_total REAL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES usuarios(id),
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);

CREATE TABLE clientes (
    id INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    telefone TEXT,
    cpf TEXT UNIQUE NOT NULL,
    endereco TEXT,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE vehicle_photos (
    id INTEGER PRIMARY KEY,
    veiculo_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    FOREIGN KEY (veiculo_id) REFERENCES veiculos(id)
);

CREATE TABLE newsletter (
    id INTEGER PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    criado_em TEXT DEFAULT CURRENT_TIMESTAMP
);

