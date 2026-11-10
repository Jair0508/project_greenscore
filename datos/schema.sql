-- GreenScore: esquema completo de Postgres (Supabase)
-- Correr una sola vez en el SQL Editor de un proyecto nuevo.

CREATE TABLE usuarios (
    id                     VARCHAR PRIMARY KEY,      -- DNI o id alfanumérico (ej. "admin1"); incluye ceros a la izquierda
    rol                    VARCHAR NOT NULL,         -- 'admin' | 'desarrollador' | 'negocio' | 'vecino' | gestor de reciclaje: el codigo usa 3 variantes de texto ("gestor", "gestor_reciclaje", "gestor de reciclaje") segun el flujo -- sin restriccion a nivel de columna
    nombre                 VARCHAR NOT NULL,
    correo                 VARCHAR,
    clave                  VARCHAR NOT NULL,         -- texto plano por ahora
    telefono               VARCHAR,
    puntos                 NUMERIC,                  -- NULL para roles no-vecino
    suspendido             BOOLEAN NOT NULL DEFAULT FALSE,
    motivo_suspension      TEXT NOT NULL DEFAULT '',
    justificacion_cliente  TEXT NOT NULL DEFAULT '',
    pregunta_secreta       VARCHAR,
    respuesta_secreta      VARCHAR,
    reciclaje_activo       BOOLEAN NOT NULL DEFAULT TRUE  -- solo aplica a rol 'negocio', activa/desactiva punto de entrega
);

CREATE TABLE log_clientes (
    id            SERIAL PRIMARY KEY,
    fecha         TIMESTAMP NOT NULL DEFAULT NOW(),
    dni_cliente   VARCHAR NOT NULL REFERENCES usuarios(id),
    tipo          VARCHAR NOT NULL,
    puntos        NUMERIC NOT NULL,
    detalle       TEXT
);

CREATE TABLE log_desarrolladores (
    id            SERIAL PRIMARY KEY,
    fecha         TIMESTAMP NOT NULL DEFAULT NOW(),
    autor_id      VARCHAR NOT NULL REFERENCES usuarios(id),
    autor_nombre  VARCHAR NOT NULL,
    accion        VARCHAR NOT NULL,
    objetivo      TEXT
);

CREATE TABLE log_tiendas (
    id                  SERIAL PRIMARY KEY,
    fecha               TIMESTAMP NOT NULL DEFAULT NOW(),
    tienda_id           VARCHAR NOT NULL REFERENCES usuarios(id),
    tienda_nombre       VARCHAR NOT NULL,
    dni_cliente         VARCHAR NOT NULL REFERENCES usuarios(id),
    puntos_descontados  NUMERIC NOT NULL
);

CREATE TABLE promociones (
    id            SERIAL PRIMARY KEY,             -- antes se identificaba por indice de lista
    tienda_id     VARCHAR NOT NULL REFERENCES usuarios(id),
    tienda_nombre VARCHAR NOT NULL,
    titulo        VARCHAR NOT NULL,
    categoria     VARCHAR,
    descripcion   VARCHAR,
    precio_soles  NUMERIC NOT NULL,
    puntos        NUMERIC NOT NULL,
    foto          TEXT,
    stock         INTEGER
);

CREATE TABLE entregas (
    id            SERIAL PRIMARY KEY,
    fecha         TIMESTAMP NOT NULL DEFAULT NOW(),
    tienda_id     VARCHAR NOT NULL REFERENCES usuarios(id),
    dni_cliente   VARCHAR NOT NULL REFERENCES usuarios(id),
    material      VARCHAR NOT NULL,
    peso_kg       NUMERIC NOT NULL,
    puntos        INTEGER NOT NULL
);

CREATE TABLE chat (
    id            SERIAL PRIMARY KEY,
    fecha         TIMESTAMP NOT NULL DEFAULT NOW(),
    dni_cliente   VARCHAR NOT NULL REFERENCES usuarios(id),
    autor         VARCHAR NOT NULL,
    rol           VARCHAR NOT NULL,
    mensaje       TEXT NOT NULL,
    leido         BOOLEAN NOT NULL DEFAULT FALSE
);
