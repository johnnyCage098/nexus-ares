
import requests
from datetime import date
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST


def inicio(request):
    ordenes = []
    error = None

    try:
        respuesta = requests.get(
            f"{settings.API_URL}/api/ordenes",
            timeout=10
        )
        respuesta.raise_for_status()
        ordenes = respuesta.json()
    except requests.RequestException:
        error = "No fue posible conectar con la API Flask."

    return render(request, "ordenes/inicio.html", {
        "ordenes": ordenes,
        "error": error,
    })


@require_POST
def crear_orden(request):
    datos = {
        "cliente": request.POST.get("cliente", "").strip(),
        "fecha": request.POST.get("fecha") or date.today().isoformat(),
        "estado": request.POST.get("estado", "Pendiente")
    }

    try:
        respuesta = requests.post(
            f"{settings.API_URL}/api/ordenes",
            json=datos,
            timeout=10
        )
        respuesta.raise_for_status()
        messages.success(request, "Orden creada correctamente.")
    except requests.RequestException:
        messages.error(request, "Error al crear la orden.")

    return redirect("inicio")


@require_POST
def editar_orden(request, orden_id):
    datos = {
        "cliente": request.POST.get("cliente", "").strip(),
        "fecha": request.POST.get("fecha"),
        "estado": request.POST.get("estado", "Pendiente")
    }

    try:
        respuesta = requests.put(
            f"{settings.API_URL}/api/ordenes/{orden_id}",
            json=datos,
            timeout=10
        )
        respuesta.raise_for_status()
        messages.success(request, "Orden actualizada correctamente.")
    except requests.RequestException:
        messages.error(request, "Error al actualizar la orden.")

    return redirect("inicio")


@require_POST
def eliminar_orden(request, orden_id):
    try:
        respuesta = requests.delete(
            f"{settings.API_URL}/api/ordenes/{orden_id}",
            timeout=10
        )
        respuesta.raise_for_status()
        messages.success(request, "Orden eliminada correctamente.")
    except requests.RequestException:
        messages.error(request, "Error al eliminar la orden.")

    return redirect("inicio")

@require_POST
def agregar_producto(request, orden_id):
    datos = {
        "producto": request.POST.get("producto", "").strip(),
        "cantidad": request.POST.get("cantidad", "1"),
        "precio_unitario": request.POST.get("precio_unitario", "0")
    }

    try:
        respuesta = requests.post(
            f"{settings.API_URL}/api/ordenes/{orden_id}/detalles",
            json=datos,
            timeout=10
        )
        respuesta.raise_for_status()
        messages.success(request, "Producto agregado correctamente.")
    except requests.RequestException:
        messages.error(request, "No se pudo agregar el producto.")

    return redirect("inicio")
