
SET QUOTED_IDENTIFIER ON;
GO
SET ANSI_NULLS ON;
GO

IF DB_ID('OrdenesDB') IS NULL
    CREATE DATABASE OrdenesDB;
GO

USE OrdenesDB;
GO

IF OBJECT_ID('dbo.ordenes', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.ordenes (
        id INT IDENTITY(1,1) PRIMARY KEY,
        cliente NVARCHAR(150) NOT NULL,
        fecha DATE NOT NULL DEFAULT CAST(GETDATE() AS DATE),
        estado NVARCHAR(20) NOT NULL DEFAULT 'Pendiente',
        total DECIMAL(12,2) NOT NULL DEFAULT 0,
        CONSTRAINT CK_ordenes_estado
            CHECK (estado IN ('Pendiente', 'Pagada', 'Anulada'))
    );
END;
GO

IF OBJECT_ID('dbo.orden_detalle', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.orden_detalle (
        id INT IDENTITY(1,1) PRIMARY KEY,
        orden_id INT NOT NULL,
        producto NVARCHAR(150) NOT NULL,
        cantidad INT NOT NULL,
        precio_unitario DECIMAL(12,2) NOT NULL,
        subtotal AS (CAST(cantidad * precio_unitario AS DECIMAL(12,2))) PERSISTED,
        CONSTRAINT FK_detalle_orden
            FOREIGN KEY (orden_id) REFERENCES dbo.ordenes(id)
            ON DELETE CASCADE,
        CONSTRAINT CK_cantidad CHECK (cantidad > 0),
        CONSTRAINT CK_precio CHECK (precio_unitario >= 0)
    );
END;
GO

IF NOT EXISTS (SELECT 1 FROM dbo.ordenes)
BEGIN
    INSERT INTO dbo.ordenes (cliente, fecha, estado)
    VALUES
    ('Carlos Lopez', '2026-11-17', 'Pagada'),
    ('Ana Martinez', '2026-11-17', 'Pendiente'),
    ('Luis Perez', '2026-11-17', 'Pagada'),
    ('Maria Rodriguez', '2026-11-17', 'Pendiente'),
    ('Pedro Gomez', '2026-11-17', 'Anulada');

    INSERT INTO dbo.orden_detalle
        (orden_id, producto, cantidad, precio_unitario)
    VALUES
    (1, 'Teclado mecanico', 2, 650.00),
    (1, 'Mouse gamer', 1, 450.00),
    (2, 'Monitor LED', 1, 3500.00),
    (2, 'Cable HDMI', 2, 180.00),
    (3, 'Memoria USB', 3, 250.00),
    (3, 'Audifonos', 1, 1200.00),
    (4, 'Disco SSD', 1, 1850.00),
    (4, 'Adaptador USB', 2, 175.00),
    (5, 'Webcam HD', 1, 950.00),
    (5, 'Soporte laptop', 1, 600.00);
END;
GO

UPDATE o
SET total = ISNULL((
    SELECT SUM(d.subtotal)
    FROM dbo.orden_detalle d
    WHERE d.orden_id = o.id
), 0)
FROM dbo.ordenes o;
GO

SELECT * FROM dbo.ordenes;
SELECT * FROM dbo.orden_detalle;
GO
