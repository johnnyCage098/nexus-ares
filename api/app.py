import os
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

import pymssql
from flask import Flask, jsonify, request

app = Flask(__name__)


# Conexion con SQL Server
def conexion():
    return pymssql.connect(
        server=os.getenv("DB_HOST", "db"),
        user="sa",
        password=os.environ["MSSQL_SA_PASSWORD"],
        database=os.getenv("DB_NAME", "OrdenesDB"),
        as_dict=True,
        timeout=10
    )


# Convertir fechas y valores decimales a JSON
def convertir(valor):
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    return valor


def normalizar(filas):
    return [
        {clave: convertir(valor) for clave, valor in fila.items()}
        for fila in filas
    ]


# Actualizar el total de una orden
def recalcular(cursor, orden_id):
    cursor.execute("""
        UPDATE ordenes
        SET total = COALESCE((
            SELECT SUM(subtotal)
            FROM orden_detalle
            WHERE orden_id = %s
        ), 0)
        WHERE id = %s
    """, (orden_id, orden_id))


# Comprobar que la API y SQL Server funcionan
@app.get("/health")
def health():
    db = None
    try:
        db = conexion()
        cursor = db.cursor()
        cursor.execute("SELECT 1 AS prueba")
        cursor.fetchone()

        return jsonify({
            "estado": "ok",
            "servicio": "NEXUS ARES API"
        }), 200

    except Exception as error:
        app.logger.error("Error de conexion: %s", error)
        return jsonify({
            "estado": "error",
            "mensaje": "No se pudo conectar con SQL Server"
        }), 503

    finally:
        if db is not None:
            db.close()


# Listar todas las ordenes
@app.get("/api/ordenes")
def listar_ordenes():
    with conexion() as db:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM ordenes ORDER BY id")
        return jsonify(normalizar(cursor.fetchall()))


# Consultar una orden con sus productos
@app.get("/api/ordenes/<int:orden_id>")
def obtener_orden(orden_id):
    with conexion() as db:
        cursor = db.cursor()
        cursor.execute(
            "SELECT * FROM ordenes WHERE id = %s",
            (orden_id,)
        )
        orden = cursor.fetchone()

        if not orden:
            return jsonify({
                "error": "Orden no encontrada"
            }), 404

        cursor.execute("""
            SELECT * FROM orden_detalle
            WHERE orden_id = %s
            ORDER BY id
        """, (orden_id,))

        orden = normalizar([orden])[0]
        orden["detalles"] = normalizar(cursor.fetchall())

        return jsonify(orden)


# Crear una nueva orden
@app.post("/api/ordenes")
def crear_orden():
    datos = request.get_json(silent=True) or {}

    cliente = str(datos.get("cliente", "")).strip()

    if not cliente:
        return jsonify({
            "error": "El cliente es obligatorio"
        }), 400

    with conexion() as db:
        cursor = db.cursor()

        cursor.execute("""
            INSERT INTO ordenes (cliente, fecha, estado)
            OUTPUT INSERTED.id
            VALUES (%s, %s, %s)
        """, (
            cliente,
            datos.get("fecha", date.today().isoformat()),
            datos.get("estado", "Pendiente")
        ))

        nuevo_id = cursor.fetchone()["id"]
        db.commit()

    return jsonify({
        "id": nuevo_id,
        "mensaje": "Orden creada correctamente"
    }), 201


# Editar una orden existente
@app.put("/api/ordenes/<int:orden_id>")
def editar_orden(orden_id):
    datos = request.get_json(silent=True) or {}

    with conexion() as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM ordenes WHERE id = %s",
            (orden_id,)
        )
        actual = cursor.fetchone()

        if not actual:
            return jsonify({
                "error": "Orden no encontrada"
            }), 404

        cliente = str(
            datos.get("cliente", actual["cliente"])
        ).strip()

        if not cliente:
            return jsonify({
                "error": "El cliente es obligatorio"
            }), 400

        cursor.execute("""
            UPDATE ordenes
            SET cliente = %s, fecha = %s, estado = %s
            WHERE id = %s
        """, (
            cliente,
            datos.get("fecha", actual["fecha"]),
            datos.get("estado", actual["estado"]),
            orden_id
        ))

        db.commit()

    return jsonify({
        "mensaje": "Orden actualizada correctamente"
    }), 200


# Eliminar una orden y sus detalles
@app.delete("/api/ordenes/<int:orden_id>")
def eliminar_orden(orden_id):
    with conexion() as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = %s",
            (orden_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "Orden no encontrada"
            }), 404

        cursor.execute(
            "DELETE FROM orden_detalle WHERE orden_id = %s",
            (orden_id,)
        )

        cursor.execute(
            "DELETE FROM ordenes WHERE id = %s",
            (orden_id,)
        )

        db.commit()

    return jsonify({
        "mensaje": "Orden eliminada correctamente"
    }), 200


# Listar o agregar productos a una orden
@app.route(
    "/api/ordenes/<int:orden_id>/detalles",
    methods=["GET", "POST"]
)
def detalles_orden(orden_id):
    with conexion() as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT id FROM ordenes WHERE id = %s",
            (orden_id,)
        )

        if not cursor.fetchone():
            return jsonify({
                "error": "Orden no encontrada"
            }), 404

        if request.method == "GET":
            cursor.execute("""
                SELECT * FROM orden_detalle
                WHERE orden_id = %s
                ORDER BY id
            """, (orden_id,))

            return jsonify(normalizar(cursor.fetchall()))

        datos = request.get_json(silent=True) or {}

        try:
            producto = str(datos["producto"]).strip()
            cantidad = int(datos["cantidad"])
            precio = Decimal(str(datos["precio_unitario"]))

            if (
                not producto
                or cantidad <= 0
                or not precio.is_finite()
                or precio < 0
            ):
                raise ValueError()

        except (
            KeyError, ValueError, TypeError,
            InvalidOperation, ArithmeticError
        ):
            return jsonify({
                "error": "Datos del producto invalidos"
            }), 400

        cursor.execute("""
            INSERT INTO orden_detalle
                (orden_id, producto, cantidad, precio_unitario)
            OUTPUT INSERTED.id
            VALUES (%s, %s, %s, %s)
        """, (
            orden_id,
            producto,
            cantidad,
            precio
        ))

        nuevo_id = cursor.fetchone()["id"]

        recalcular(cursor, orden_id)
        db.commit()

        return jsonify({
            "id": nuevo_id,
            "mensaje": "Producto agregado correctamente"
        }), 201


# Editar o eliminar un producto
@app.route(
    "/api/detalles/<int:detalle_id>",
    methods=["PUT", "DELETE"]
)
def modificar_detalle(detalle_id):
    with conexion() as db:
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM orden_detalle WHERE id = %s",
            (detalle_id,)
        )

        actual = cursor.fetchone()

        if not actual:
            return jsonify({
                "error": "Detalle no encontrado"
            }), 404

        orden_id = actual["orden_id"]

        if request.method == "DELETE":
            cursor.execute(
                "DELETE FROM orden_detalle WHERE id = %s",
                (detalle_id,)
            )

        else:
            datos = request.get_json(silent=True) or {}

            try:
                producto = str(
                    datos.get("producto", actual["producto"])
                ).strip()

                cantidad = int(
                    datos.get("cantidad", actual["cantidad"])
                )

                precio = Decimal(str(
                    datos.get(
                        "precio_unitario",
                        actual["precio_unitario"]
                    )
                ))

                if (
                    not producto
                    or cantidad <= 0
                    or not precio.is_finite()
                    or precio < 0
                ):
                    raise ValueError()

            except (
                ValueError, TypeError,
                InvalidOperation, ArithmeticError
            ):
                return jsonify({
                    "error": "Datos invalidos"
                }), 400

            cursor.execute("""
                UPDATE orden_detalle
                SET producto = %s,
                    cantidad = %s,
                    precio_unitario = %s
                WHERE id = %s
            """, (
                producto,
                cantidad,
                precio,
                detalle_id
            ))

        recalcular(cursor, orden_id)
        db.commit()

    return jsonify({
        "mensaje": "Operacion realizada correctamente"
    }), 200


# Manejo de errores internos
@app.errorhandler(500)
def error_servidor(error):
    return jsonify({
        "error": "Error interno del servidor"
    }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
