/* ============================================================
   Arquivo: 90_verificacoes_pos_execucao.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Conferir integridade e contagens
============================================================ */

SELECT COUNT(*) AS total_usuarios FROM usuarios;
SELECT COUNT(*) AS total_veiculos FROM veiculos;
SELECT COUNT(*) AS total_reservas FROM reservas;
SELECT modelo, status FROM veiculos;
SELECT * FROM vw_calculo_locacao;

