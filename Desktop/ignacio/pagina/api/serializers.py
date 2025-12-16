# api/serializers.py
from rest_framework import serializers
from django.db import transaction
from .models import Empresa, Cliente, TipoProducto, Producto, MovimientoInventario

class EmpresaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Empresa
        fields = '__all__'

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = '__all__'

class TipoProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipoProducto
        fields = '__all__'

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = '__all__'

        read_only_fields = ['empresa'] 


    def validate_stock_actual(self, value):
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value

    def validate_precio_venta(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio de venta no puede ser negativo.")
        return value

    def validate_precio_compra(self, value):
        if value < 0:
            raise serializers.ValidationError("El precio de compra no puede ser negativo.")
        return value

class MovimientoInventarioSerializer(serializers.ModelSerializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())

    class Meta:
        model = MovimientoInventario
        fields = '__all__'
        read_only_fields = ('fecha_hora', 'id_movimiento')

    def validate_cantidad(self, value):
        if value is None or value <= 0:
            raise serializers.ValidationError("La cantidad debe ser mayor que cero.")
        return value

    def validate(self, attrs):
        producto = attrs.get('producto')
        tipo = attrs.get('tipo_movimiento')
        cantidad = attrs.get('cantidad')

        if tipo not in dict(MovimientoInventario.TIPO_CHOICES):
            raise serializers.ValidationError({"tipo_movimiento": "Tipo inválido."})

        # Comprobación preliminar (la verificación definitiva se hace con lock en create)
        if tipo == 'salida' and producto and cantidad is not None:
            if producto.stock_actual - cantidad < 0:
                raise serializers.ValidationError({"cantidad": "Stock insuficiente para esta salida."})
        return attrs

    def create(self, validated_data):
        producto = validated_data['producto']
        tipo = validated_data['tipo_movimiento']
        cantidad = validated_data['cantidad']

        # Operación atómica y bloqueo de fila del producto
        with transaction.atomic():
            producto_locked = Producto.objects.select_for_update().get(pk=producto.pk)

            # Revalidar stock bajo lock
            if tipo == 'salida' and producto_locked.stock_actual - cantidad < 0:
                raise serializers.ValidationError({"cantidad": "Stock insuficiente para esta salida."})

            # Ajustar stock
            if tipo == 'ingreso':
                producto_locked.stock_actual += cantidad
            else:  # 'salida' o 'ajuste'
                producto_locked.stock_actual -= abs(cantidad)
            producto_locked.save()

            movimiento = MovimientoInventario.objects.create(**validated_data)
        return movimiento
