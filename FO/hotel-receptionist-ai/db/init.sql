-- Inicialización de la base de datos del hotel

-- Tabla de tipos de habitación
CREATE TABLE IF NOT EXISTS room_types (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    base_price DECIMAL(10,2) NOT NULL,
    max_guests INTEGER NOT NULL,
    amenities JSONB,
    available_count INTEGER DEFAULT 0,
    image_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar tipos de habitación de ejemplo
INSERT INTO room_types (name, description, base_price, max_guests, amenities) VALUES
('Estándar', 'Habitación cómoda con cama doble, baño privado y TV', 89.99, 2, '["WiFi", "TV", "Aire acondicionado", "Baño privado"]'),
('Deluxe', 'Habitación espaciosa con vista, minibar y jacuzzi', 149.99, 3, '["WiFi", "TV", "Minibar", "Jacuzzi", "Vista"]'),
('Suite', 'Suite de lujo con sala separada y servicios premium', 249.99, 4, '["WiFi", "TV 55''", "Minibar", "Jacuzzi", "Vista", "Room service 24h"]');

-- Tabla de huéspedes
CREATE TABLE IF NOT EXISTS guests (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    country VARCHAR(100),
    language_preference VARCHAR(10) DEFAULT 'es',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de reservas
CREATE TABLE IF NOT EXISTS reservations (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    guest_id VARCHAR(36) REFERENCES guests(id) ON DELETE CASCADE,
    room_type VARCHAR(50) NOT NULL,
    check_in_date TIMESTAMP NOT NULL,
    check_out_date TIMESTAMP NOT NULL,
    number_of_guests INTEGER NOT NULL,
    special_requests TEXT,
    status VARCHAR(20) DEFAULT 'confirmed',
    total_price DECIMAL(10,2) NOT NULL,
    payment_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de llamadas registradas
CREATE TABLE IF NOT EXISTS call_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    caller_number VARCHAR(20) NOT NULL,
    call_duration INTEGER,
    intent_detected VARCHAR(100),
    resolution_status VARCHAR(50),
    recording_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para mejor rendimiento
CREATE INDEX idx_reservations_guest_id ON reservations(guest_id);
CREATE INDEX idx_reservations_dates ON reservations(check_in_date, check_out_date);
CREATE INDEX idx_call_logs_date ON call_logs(created_at);
CREATE INDEX idx_guests_email ON guests(email);

-- Conversaciones por número (estado del flujo)
CREATE TABLE IF NOT EXISTS message_threads (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL DEFAULT 'sms', -- sms | whatsapp
    state VARCHAR(50) NOT NULL DEFAULT 'idle',  -- idle | awaiting_dates | awaiting_pax | done
    context JSONB NOT NULL DEFAULT '{}'::jsonb, -- datos parciales (dates, pax, etc.)
    last_intent VARCHAR(50),
    last_message_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_message_threads_phone_channel
ON message_threads (phone_number, channel);

-- Log de mensajes entrantes / salientes
CREATE TABLE IF NOT EXISTS message_logs (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid(),
    phone_number VARCHAR(20) NOT NULL,
    channel VARCHAR(20) NOT NULL DEFAULT 'sms',
    direction VARCHAR(10) NOT NULL, -- inbound | outbound
    body TEXT,
    twilio_message_sid VARCHAR(64),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_message_logs_phone_date
ON message_logs (phone_number, created_at);

