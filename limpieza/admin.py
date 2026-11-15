from django.contrib import admin

from .models import (
    Limpiador,
    PerfilLimpiador,
    Centro,
    Aseo,
    Turno,
    Cuadrante,
    Fichaje,
    Producto,
    Inventario,
    Limpieza,
)

admin.site.register(Limpiador)
admin.site.register(PerfilLimpiador)
admin.site.register(Centro)
admin.site.register(Aseo)
admin.site.register(Turno)
admin.site.register(Cuadrante)
admin.site.register(Fichaje)
admin.site.register(Producto)
admin.site.register(Inventario)
admin.site.register(Limpieza)
