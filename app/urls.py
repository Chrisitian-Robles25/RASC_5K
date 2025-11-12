from django.urls import path
from .views import LoginView, LogoutView, RefreshTokenView, EnviarTiemposView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('enviar_tiempos/', EnviarTiemposView.as_view(), name='enviar_tiempos'),
]
