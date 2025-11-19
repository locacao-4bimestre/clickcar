/* ============================================================
   Arquivo: 11_queries_relatorios.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Consultas avançadas (relatórios)
============================================================ */

-- Veículos mais alugados
SELECT v.modelo, COUNT(r.id) AS total
FROM veiculos v
JOIN reservas r ON r.veiculo_id = v.id
GROUP BY v.id
ORDER BY total DESC;

-- Faturamento (somente reservas que possuem valor_total)
SELECT SUM(valor_total) AS faturamento FROM reservas;

-- Reservas de fevereiro de 2025
SELECT * FROM reservas
WHERE substr(data_inicio, 6, 2) = '02'
AND substr(data_inicio, 1, 4) = '2025';


