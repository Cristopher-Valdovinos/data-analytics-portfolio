-- ====================================================================
-- PROYECTO: ANÁLISIS DE VENTAS, MARGEN Y SEGMENTACIÓN COMERCIAL
-- AUTOR: Cristopher Valdovinos (Ingeniero Comercial & Data Analyst)
-- MOTOR: MySQL
-- ====================================================================

-- 1. CREACIÓN DEL ESQUEMA Y TABLAS
CREATE SCHEMA IF NOT EXISTS retail_analytics;
USE retail_analytics;

-- Tabla de Clientes
CREATE TABLE IF NOT EXISTS clientes (
    cliente_id INT PRIMARY KEY,
    nombre VARCHAR(100),
    segmento VARCHAR(50),
    ciudad VARCHAR(50)
);

-- Tabla de Productos
CREATE TABLE IF NOT EXISTS productos (
    producto_id INT PRIMARY KEY,
    nombre_producto VARCHAR(100),
    categoria VARCHAR(50),
    costo_unitario DECIMAL(10,2),
    precio_unitario DECIMAL(10,2)
);

-- Tabla de Ventas (Hechos)
CREATE TABLE IF NOT EXISTS ventas (
    venta_id INT PRIMARY KEY,
    fecha_venta DATE,
    cliente_id INT,
    producto_id INT,
    cantidad INT,
    FOREIGN KEY (cliente_id) REFERENCES clientes(cliente_id),
    FOREIGN KEY (producto_id) REFERENCES productos(producto_id)
);

-- 2. POBLADO DE DATOS (MUESTRA DE CONTROL DE GESTIÓN)
INSERT INTO clientes VALUES
(1, 'Empresa Alfa SpA', 'Corporativo', 'Santiago'),
(2, 'Servicios Beta Ltda', 'Pyme', 'Valparaíso'),
(3, 'Comercial Gamma', 'Corporativo', 'Concepción'),
(4, 'Distribuidora Delta', 'Pyme', 'Santiago'),
(5, 'Inversiones Epsilon', 'Corporativo', 'Antofagasta');

INSERT INTO productos VALUES
(101, 'Monitor Curvo 27"', 'Tecnología', 120.00, 210.00),
(102, 'Teclado Mecánico', 'Accesorios', 30.00, 65.00),
(103, 'Silla Ergonómica', 'Mobiliario', 85.00, 160.00),
(104, 'Laptop Ejecutiva 16GB', 'Tecnología', 450.00, 780.00),
(105, 'Hub USB-C Multipuerto', 'Accesorios', 15.00, 40.00);

INSERT INTO ventas VALUES
(1001, '2026-01-10', 1, 104, 5),
(1002, '2026-01-12', 2, 102, 10),
(1003, '2026-01-15', 3, 101, 8),
(1004, '2026-01-20', 1, 103, 4),
(1005, '2026-02-05', 4, 105, 20),
(1006, '2026-02-14', 5, 104, 3),
(1007, '2026-02-18', 2, 101, 6),
(1008, '2026-03-01', 3, 104, 4),
(1009, '2026-03-10', 1, 102, 15),
(1010, '2026-03-15', 5, 103, 7);

-- ====================================================================
-- 3. CONSULTAS ANALÍTICAS PARA TOMA DE DECISIONES
-- ====================================================================

-- KPI 1: Ingresos totales, costos y margen bruto por categoría de producto
SELECT 
    p.categoria,
    SUM(v.cantidad * p.precio_unitario) AS ingresos_totales,
    SUM(v.cantidad * p.costo_unitario) AS costos_totales,
    SUM(v.cantidad * (p.precio_unitario - p.costo_unitario)) AS margen_bruto,
    ROUND(
        (SUM(v.cantidad * (p.precio_unitario - p.costo_unitario)) / SUM(v.cantidad * p.precio_unitario)) * 100, 
        2
    ) AS margen_porcentual
FROM ventas v
JOIN productos p ON v.producto_id = p.producto_id
GROUP BY p.categoria
ORDER BY margen_bruto DESC;

-- KPI 2: Ranking de clientes por facturación (Uso de Funciones de Ventana / Window Functions)
SELECT 
    c.nombre AS cliente,
    c.segmento,
    c.ciudad,
    SUM(v.cantidad * p.precio_unitario) AS total_facturado,
    DENSE_RANK() OVER (ORDER BY SUM(v.cantidad * p.precio_unitario) DESC) AS ranking_ventas
FROM ventas v
JOIN clientes c ON v.cliente_id = c.cliente_id
JOIN productos p ON v.producto_id = p.producto_id
GROUP BY c.cliente_id, c.nombre, c.segmento, c.ciudad;

-- KPI 3: Análisis mensual y evolución de ticket promedio
WITH resumen_mensual AS (
    SELECT 
        DATE_FORMAT(v.fecha_venta, '%Y-%m') AS mes,
        COUNT(DISTINCT v.venta_id) AS transacciones,
        SUM(v.cantidad * p.precio_unitario) AS facturacion_mensual
    FROM ventas v
    JOIN productos p ON v.producto_id = p.producto_id
    GROUP BY DATE_FORMAT(v.fecha_venta, '%Y-%m')
)
SELECT 
    mes,
    transacciones,
    facturacion_mensual,
    ROUND(facturacion_mensual / transacciones, 2) AS ticket_promedio
FROM resumen_mensual
ORDER BY mes ASC;
