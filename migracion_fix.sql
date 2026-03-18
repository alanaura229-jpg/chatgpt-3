-- ════════════════════════════════════════════════════════════════════════
--  BTU-UASLP — Migración: ampliar columnas demasiado cortas
--  Ejecutar en MySQL una sola vez
-- ════════════════════════════════════════════════════════════════════════

USE btu_uaslp;

-- Columnas que causaban el error "Data too long"
ALTER TABLE usuario
    MODIFY COLUMN sexo               VARCHAR(30)  NULL,
    MODIFY COLUMN telefono           VARCHAR(30)  NULL,
    MODIFY COLUMN nacionalidad       VARCHAR(80)  NULL,
    MODIFY COLUMN pais_origen        VARCHAR(100) NULL,
    MODIFY COLUMN tipo_usuario       VARCHAR(30)  NOT NULL,
    MODIFY COLUMN modalidad_estudio  VARCHAR(50)  NULL,
    MODIFY COLUMN carrera            VARCHAR(150) NULL,
    MODIFY COLUMN facultad           VARCHAR(150) NULL,
    MODIFY COLUMN area               VARCHAR(150) NULL,
    MODIFY COLUMN programa_academico VARCHAR(200) NULL,
    MODIFY COLUMN nombre_empresa     VARCHAR(200) NULL,
    MODIFY COLUMN giro_empresa       VARCHAR(150) NULL,
    MODIFY COLUMN puesto             VARCHAR(150) NULL,
    MODIFY COLUMN nombre_coord       VARCHAR(250) NULL,
    MODIFY COLUMN cargo_coord        VARCHAR(150) NULL,
    MODIFY COLUMN tipo_entidad_coord VARCHAR(50)  NULL,
    MODIFY COLUMN cv_filename        VARCHAR(300) NULL,
    MODIFY COLUMN reset_token        VARCHAR(150) NULL,
    MODIFY COLUMN dos_pasos_codigo   VARCHAR(20)  NULL;

SELECT 'Migración aplicada correctamente.' AS resultado;
