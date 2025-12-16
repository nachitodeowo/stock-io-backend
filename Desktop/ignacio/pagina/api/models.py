# api/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 

class Empresa(models.Model):
    id_empresa = models.AutoField(primary_key=True)
    rut_empresa = models.CharField(max_length=20, unique=True)
    razon_social = models.CharField(max_length=255)
    nombre = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    plan_contratado = models.CharField(max_length=100, blank=True)
    estado_servicio = models.CharField(max_length=50, default='activo')
    fecha_inicio_contrato = models.DateField(null=True, blank=True)
    fecha_proximo_pago = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.razon_social} ({self.rut_empresa})"

class Cliente(models.Model):
    run = models.CharField(max_length=20)
    emp = models.ForeignKey(Empresa, related_name='clientes', on_delete=models.CASCADE)
    nombre = models.CharField(max_length=255)
    edad = models.PositiveIntegerField(null=True, blank=True)
    telefono = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.nombre} - {self.run}"

class TipoProducto(models.Model):
    id_tipo = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    es_perecedero = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    codigop = models.AutoField(primary_key=True)
    empresa = models.ForeignKey(Empresa, related_name='productos', on_delete=models.CASCADE)
    tipo = models.ForeignKey(TipoProducto, related_name='productos', on_delete=models.SET_NULL, null=True, blank=True)
    nombre = models.CharField(max_length=255)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    precio_venta = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    precio_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    stock_actual = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigop})"

    def ajustar_stock(self, cantidad):
        self.stock_actual += cantidad
        self.save()

# En api/models.py

class MovimientoInventario(models.Model):
    id_movimiento = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, related_name='movimientos', on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(default=timezone.now)
    TIPO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('salida', 'Salida'),
        ('ajuste', 'Ajuste'),
    ]
    tipo_movimiento = models.CharField(max_length=20, choices=TIPO_CHOICES)
    cantidad = models.IntegerField()

    # 👇 HE BORRADO LA LÓGICA DE RESTA AQUÍ.
    # Ahora solo guardamos el movimiento. 
    # La resta matemática la hace tu Serializer (que es más seguro).
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.tipo_movimiento} {self.cantidad} - {self.producto.nombre}"


class Empleado(models.Model):
    # Relacionamos el Usuario de Django (Login) con la Empresa
    usuario = models.OneToOneField(User, on_delete=models.CASCADE) 
    empresa = models.ForeignKey(Empresa, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usuario.username} - {self.empresa.razon_social}"
