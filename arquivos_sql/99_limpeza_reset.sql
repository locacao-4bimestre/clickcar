/* ============================================================
   Arquivo: 99_limpeza_reset.sql (opcional)
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Reset completo do banco
   AVISO: Apaga todos os dados!
============================================================ */

DELETE FROM reservas;
DELETE FROM clientes;
DELETE FROM usuarios;
DELETE FROM veiculos;

