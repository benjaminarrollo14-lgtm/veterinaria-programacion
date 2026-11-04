-- C-08 · La base rechaza un precio de 0 por el CHECK (ck_practica_precio_positivo).
-- Correr después de crear al menos una práctica, por ejemplo:
--   psql "$DATABASE_PSQL" -f test/c08_precio_cero.sql
-- Esperado: ERROR: new row for relation "practica" violates check constraint "ck_practica_precio_positivo"
UPDATE practica SET precio = 0 WHERE id = 1;
