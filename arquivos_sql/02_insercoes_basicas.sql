
/* ============================================================
   Arquivo: 02_insercoes_basicas.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Inserção de dados mínimos
   Execução esperada: após 01_modelo_fisico.sql
============================================================ */

INSERT INTO perfis (nome_perfil) VALUES 
('cliente'),
('funcionario'),
('gerente');

INSERT INTO tipo_veiculo (nome, descricao) VALUES
('Sedan', 'Carro pequeno a médio'),
('SUV', 'Utilitário esportivo'),
('Pick-up', 'Caminhonete');

INSERT INTO usuarios (nome, email, senha_hash, perfil_id)
VALUES 
('Administrador', 'admin@mflex.com', 'HASH123', 3),
('João Cliente', 'cliente@mflex.com', 'HASH456', 1);

INSERT INTO veiculos (modelo, marca, ano, placa, cor, tipo_id, preco_por_dia)
VALUES 
('Corolla', 'Toyota', 2020, 'ABC-1234', 'Prata', 1, 150),
('Hilux', 'Toyota', 2022, 'XYZ-9876', 'Preta', 3, 300),
('Compass', 'Jeep', 2021, 'JKL-5678', 'Branca', 2, 220);

INSERT INTO clientes (nome, email, telefone, cpf, endereco)
VALUES
('Maria Silva', 'maria@gmail.com', '11900001111', '12345678901', 'Rua A, 123'),
('Carlos Santos', 'carlos@gmail.com', '11922223333', '98765432100', 'Rua B, 987');

