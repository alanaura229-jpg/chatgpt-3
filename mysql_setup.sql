-- ════════════════════════════════════════════════════════════════════════════
--  BTU-UASLP — Script de creación de base de datos MySQL
--  Ejecutar como root o usuario con privilegios suficientes
-- ════════════════════════════════════════════════════════════════════════════

-- 1. Crear la base de datos
CREATE DATABASE IF NOT EXISTS btu_uaslp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- 2. Crear usuario dedicado (ajusta la contraseña)
CREATE USER IF NOT EXISTS 'btu_user'@'localhost' IDENTIFIED BY 'CambiaEstaPassword123!';

-- 3. Otorgar permisos
GRANT ALL PRIVILEGES ON btu_uaslp.* TO 'btu_user'@'localhost';
FLUSH PRIVILEGES;

-- 4. Usar la base de datos
USE btu_uaslp;

-- ════════════════════════════════════════════════════════════════════════════
--  Las tablas son creadas automáticamente por SQLAlchemy al iniciar la app
--  (db.create_all() en __init__.py).
--  Este script solo crea el contenedor y el usuario.
-- ════════════════════════════════════════════════════════════════════════════

-- Opcional: usuario administrador inicial
-- (correr DESPUÉS de que SQLAlchemy haya creado las tablas)
/*
INSERT INTO usuario (
    clave_unica, email, password_hash, tipo_usuario,
    nombre, apellido_paterno, activo, aceptar_privacidad, fecha_registro
) VALUES (
    'ADMIN001',
    'admin@uaslp.mx',
    -- Genera el hash con: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('Admin1234!'))"
    'pbkdf2:sha256:...',
    'admin',
    'Administrador',
    'BTU',
    1, 1, NOW()
);
*/
