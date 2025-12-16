# api/urls.py
from django.urls import path, include
from rest_framework import routers

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    EmpresaViewSet, ClienteViewSet, TipoProductoViewSet,
    ProductoViewSet, MovimientoInventarioViewSet, user_info
)

router = routers.DefaultRouter()
router.register(r'empresas', EmpresaViewSet, basename='empresa')
router.register(r'clientes', ClienteViewSet)
router.register(r'tipos-producto', TipoProductoViewSet)
router.register(r'products', ProductoViewSet)
router.register(r'movimientos', MovimientoInventarioViewSet)

urlpatterns = [
    path('', include(router.urls)), 
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-info/', user_info, name='user_info'),
]