-- Agrega rol admin al ENUM (en transacción separada)
ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'admin';
