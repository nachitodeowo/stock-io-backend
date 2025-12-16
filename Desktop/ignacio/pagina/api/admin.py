# api/admin.py
from django.contrib import admin
from .models import Empresa, Cliente, TipoProducto, Producto, MovimientoInventario, Empleado

admin.site.register(Empresa)
admin.site.register(Cliente)
admin.site.register(TipoProducto)
admin.site.register(Producto)
admin.site.register(MovimientoInventario)
admin.site.register(Empleado)