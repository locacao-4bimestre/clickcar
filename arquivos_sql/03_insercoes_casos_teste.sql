/* ============================================================
   Arquivo: 03_insercoes_casos_teste.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Inserções para cenários de teste
============================================================ */

-- Cenário A: Reserva normal
INSERT INTO reservas (user_id, veiculo_id, data_inicio, data_fim, status)
VALUES (2, 1, '2025-01-10', '2025-01-12', 'confirmada');

-- Cenário B: Reserva pendente
INSERT INTO reservas (user_id, veiculo_id, data_inicio, data_fim, status)
VALUES (2, 2, '2025-02-01', '2025-02-05', 'pendente');

-- Cenário C: veículo fica "alugado"
UPDATE veiculos SET status = 'alugado' WHERE id = 2;
