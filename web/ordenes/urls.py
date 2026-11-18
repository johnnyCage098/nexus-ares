
from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("crear/", views.crear_orden, name="crear_orden"),
    path("editar/<int:orden_id>/", views.editar_orden, name="editar_orden"),
    path("eliminar/<int:orden_id>/", views.eliminar_orden, name="eliminar_orden"),
    path("producto/<int:orden_id>/", views.agregar_producto, name="agregar_producto"),
]
