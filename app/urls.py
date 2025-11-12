from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginView,
    LogoutView,
    RefreshTokenView,
    EnviarTiemposView,
    CompetenciaViewSet,
    EquipoViewSet,
)

# Router de DRF para ViewSets
router = DefaultRouter()
router.register(r'competencias', CompetenciaViewSet, basename='competencia')
router.register(r'equipos', EquipoViewSet, basename='equipo')

urlpatterns = [
    # Autenticación
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    
    # Tiempos
    path('enviar_tiempos/', EnviarTiemposView.as_view(), name='enviar_tiempos'),
    
    # Incluir rutas del router (Competencias y Equipos)
    path('', include(router.urls)),
]
