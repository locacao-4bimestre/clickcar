/* ============================================================
   Arquivo: 20_triggers.sql
   Autores: João Paulo Queiroz Costa, Vitória Xavieer Pereira
   Turma: 231 DS
   SGBD: SQLite 3
   Objetivo: Triggers de regras de negócio
============================================================ */

-- Ao criar reserva, mudar status do veículo para 'alugado'
CREATE TRIGGER trg_reserva_aluga
AFTER INSERT ON reservas
BEGIN
    UPDATE veiculos SET status = 'alugado'
    WHERE id = NEW.veiculo_id;
END;

-- Ao apagar reserva, liberar veículo
CREATE TRIGGER trg_reserva_libera
AFTER DELETE ON reservas
BEGIN
    UPDATE veiculos SET status = 'disponivel'
    WHERE id = OLD.veiculo_id;
END;

