/* ============================================================
   Arquivo: 10_queries_basicas.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Consultas básicas
============================================================ */

-- Listar todos os veículos
SELECT * FROM veiculos;

-- JOIN com tipo do veículo
SELECT v.modelo, v.marca, t.nome AS tipo
FROM veiculos v
JOIN tipo_veiculo t ON t.id = v.tipo_id;

-- Clientes filtrados
SELECT * FROM clientes WHERE nome LIKE '%Maria%';

-- Total de reservas por usuário
SELECT u.nome, COUNT(r.id) AS total_reservas
FROM usuarios u
LEFT JOIN reservas r ON r.user_id = u.id
GROUP BY u.id;

-- Veículos ordenados por preço
SELECT * FROM veiculos ORDER BY preco_por_dia DESC;
