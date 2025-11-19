/* ============================================================
   Arquivo: 21_procedures.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   OBS IMPORTANTE: SQLite NÃO suporta procedures.
   → Substituímos por VIEWS.
============================================================ */

CREATE VIEW vw_calculo_locacao AS
SELECT 
    r.id AS reserva_id,
    r.data_inicio,
    r.data_fim,
    (julianday(r.data_fim) - julianday(r.data_inicio)) 
        * v.preco_por_dia AS valor_estimado
FROM reservas r
JOIN veiculos v ON v.id = r.veiculo_id;

