from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count, F
from django.db.models.functions import TruncDate 
from django.utils import timezone 

from .models import Empresa, Cliente, TipoProducto, Producto, MovimientoInventario
from .serializers import (
    EmpresaSerializer, ClienteSerializer, TipoProductoSerializer,
    ProductoSerializer, MovimientoInventarioSerializer
)

class EmpresaViewSet(viewsets.ModelViewSet):
    serializer_class = EmpresaSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
            return Empresa.objects.all()
        try:
            mi_empresa_id = usuario.empleado.empresa.id
            return Empresa.objects.filter(id=mi_empresa_id)
        except AttributeError:
            return Empresa.objects.none()

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    permission_classes = [permissions.AllowAny]

class TipoProductoViewSet(viewsets.ModelViewSet):
    queryset = TipoProducto.objects.all()
    serializer_class = TipoProductoSerializer
    permission_classes = [permissions.AllowAny]

class ProductoViewSet(viewsets.ModelViewSet):
    queryset = Producto.objects.select_related('empresa', 'tipo').all()
    serializer_class = ProductoSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigop']
    ordering_fields = ['nombre', 'stock_actual', 'precio_venta']

    def get_queryset(self):
        usuario = self.request.user
        if usuario.is_superuser:
             return Producto.objects.select_related('empresa', 'tipo').all()
        try:
            return Producto.objects.select_related('empresa', 'tipo').filter(empresa=usuario.empleado.empresa)
        except AttributeError:
            return Producto.objects.none()

    def perform_create(self, serializer):
        try:
            serializer.save(empresa=self.request.user.empleado.empresa)
        except AttributeError:
            serializer.save()

    @action(detail=False, methods=['GET'])
    def dashboard_stats(self, request):
        import datetime
        
        productos = self.get_queryset()
        movimientos = MovimientoInventario.objects.all()
        
        if not request.user.is_superuser:
            try:
                movimientos = movimientos.filter(producto__empresa=request.user.empleado.empresa)
            except AttributeError:
                movimientos = movimientos.none()

        total_productos = productos.count()
        stock_critico = productos.filter(stock_actual__lte=10).count()
        
        hoy = timezone.now().date()
        limite = hoy + datetime.timedelta(days=7)
        por_vencer = productos.filter(tipo__es_perecedero=True, fecha_vencimiento__range=[hoy, limite]).count()
        movimientos_hoy = movimientos.filter(fecha_hora__date=hoy).count()

        data = {
            'total_productos': total_productos,
            'stock_critico': stock_critico,
            'por_vencer': por_vencer,
            'movimientos_hoy': movimientos_hoy
        }
        return Response(data)
    

class MovimientoInventarioViewSet(viewsets.ModelViewSet):
    queryset = MovimientoInventario.objects.select_related('producto', 'producto__empresa').all().order_by('-fecha_hora')
    serializer_class = MovimientoInventarioSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['producto__nombre', 'producto__codigop']
    ordering_fields = ['fecha_hora', 'cantidad']

    def get_queryset(self):
        usuario = self.request.user
        qs = super().get_queryset()

        if usuario.is_superuser:
            return qs

        try:
            empresa_del_usuario = usuario.empleado.empresa
            qs = qs.filter(producto__empresa=empresa_del_usuario)
        except AttributeError:
            return qs.none() 

        tipo = self.request.query_params.get('tipo')
        if tipo:
            qs = qs.filter(tipo_movimiento=tipo)

        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio and fecha_fin:
            qs = qs.filter(fecha_hora__range=[fecha_inicio, fecha_fin])
            
        return qs

    # 👇 AQUÍ ESTABA EL ERROR DEL DOBLE DESCUENTO
    def perform_create(self, serializer):
        # SOLO guardamos. La lógica matemática está en models.py
        serializer.save() 
        # (Eliminamos todo el bloque if/else que restaba otra vez)

    @action(detail=False, methods=['GET'])
    def reporte_ventas_producto(self, request):
        qs = self.get_queryset() 
        qs = qs.filter(tipo_movimiento='salida')

        reporte = qs.values(
            nombre_producto=F('producto__nombre'),
            codigo=F('producto__codigop')
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')

        return Response(reporte)

    @action(detail=False, methods=['GET'])
    def resumen_ventas(self, request):
        qs = self.get_queryset()
        ventas_qs = qs.filter(tipo_movimiento='salida') 

        resumen = ventas_qs.annotate(
            fecha=TruncDate('fecha_hora')
        ).values('fecha').annotate(
            n_operaciones=Count('id'),
            total_venta=Sum('cantidad')
        ).order_by('-fecha')

        return Response(resumen)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_info(request):
    usuario = request.user
    data = {
        'username': usuario.username,
        'empresa': 'Sin Empresa'
    }
    try:
        data['empresa'] = usuario.empleado.empresa.razon_social
    except AttributeError:
        pass
        
    return Response(data)