-- Base de datos para sistema parlamentario
CREATE DATABASE IF NOT EXISTS parlamentario_monitor;
USE parlamentario_monitor;

-- Tabla de diputados
CREATE TABLE diputados (
    id INT PRIMARY KEY AUTO_INCREMENT,
    diputado_id INT UNIQUE,
    nombre VARCHAR(255),
    partido VARCHAR(100),
    distrito VARCHAR(50),
    email VARCHAR(255),
    telefono VARCHAR(50),
    comisiones JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Tabla de proyectos
CREATE TABLE proyectos (
    id INT PRIMARY KEY AUTO_INCREMENT,
    proyecto_id VARCHAR(50) UNIQUE,
    titulo TEXT,
    tipo VARCHAR(50),
    fecha_ingreso DATE,
    autor_id INT,
    coautores JSON,
    estado VARCHAR(100),
    FOREIGN KEY (autor_id) REFERENCES diputados(diputado_id)
);
