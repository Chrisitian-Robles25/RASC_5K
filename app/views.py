from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import EnvioTiemposSerializer, CompetenciaSerializer, EquipoSerializer
from .models import Equipo, RegistroTiempo, Juez, Competencia



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'error': 'Se requiere username y password.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar el juez por username
        try:
            juez = Juez.objects.select_related('competencia').get(username=username)
        except Juez.DoesNotExist:
            return Response(
                {'error': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Verificar que el juez esté activo
        if not juez.activo:
            return Response(
                {'error': 'Usuario inactivo. Contacte al administrador.'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar la contraseña
        if not juez.check_password(password):
            return Response(
                {'error': 'Credenciales inválidas.'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Actualizar last_login
        from django.utils import timezone
        juez.last_login = timezone.now()
        juez.save(update_fields=['last_login'])

        # Generar tokens JWT
        refresh = RefreshToken()
        refresh['juez_id'] = juez.id
        refresh['username'] = juez.username
        
        # Datos del juez para respuesta
        juez_data = {
            'id': juez.id,
            'username': juez.username,
            'email': juez.email,
            'first_name': juez.first_name,
            'last_name': juez.last_name,
            'competencia': {
                'id': juez.competencia.id,
                'nombre': juez.competencia.nombre,
                'fecha_hora': juez.competencia.fecha_hora.isoformat(),
                'en_curso': juez.competencia.en_curso,
                'activa': juez.competencia.activa,
            },
            'activo': juez.activo,
            'telefono': juez.telefono,
        }
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'juez': juez_data,
            'message': 'Login exitoso'
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el refresh token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Agregar el refresh token a la blacklist
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response(
                {'message': 'Sesión cerrada exitosamente.'},
                status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as e:
            return Response(
                {'error': 'Token inválido o ya fue utilizado.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': f'Error al cerrar sesión: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response(
                    {'error': 'Se requiere el refresh token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear objeto RefreshToken y obtener nuevo access token
            token = RefreshToken(refresh_token)
            
            return Response({
                'access': str(token.access_token),
                'message': 'Token refrescado exitosamente'
            }, status=status.HTTP_200_OK)
            
        except TokenError as e:
            return Response(
                {'error': 'Refresh token inválido o expirado.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            return Response(
                {'error': f'Error al refrescar token: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EnviarTiemposView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):
        serializer = EnvioTiemposSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        equipo_id = serializer.validated_data['equipo_id']
        registros = serializer.validated_data['registros'][:15]

        juez = request.user

        try:
            equipo = Equipo.objects.get(pk=equipo_id)
        except Equipo.DoesNotExist:
            return Response({'detail': 'Equipo no existe.'}, status=status.HTTP_400_BAD_REQUEST)

        if equipo.juez_asignado_id != juez.id:
            return Response({'detail': 'No autorizado para enviar registros para este equipo.'}, status=status.HTTP_403_FORBIDDEN)

        created = []
        for reg in registros:
            rt = RegistroTiempo.objects.create(
                equipo=equipo,
                tiempo=reg['tiempo'],
                timestamp=reg['timestamp']
            )
            created.append(str(rt.id_registro))
        return Response({'created': created}, status=status.HTTP_201_CREATED)


# ============================================
# VIEWSETS PARA COMPETENCIAS Y EQUIPOS
# ============================================

class CompetenciaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Competencias (solo lectura)
    
    Endpoints automáticos:
    - GET /api/competencias/          -> Lista todas las competencias
    - GET /api/competencias/{id}/     -> Detalle de una competencia
    
    Filtros disponibles via query params:
    - ?activa=true/false
    - ?en_curso=true/false
    """
    queryset = Competencia.objects.all().order_by('-fecha_hora')
    serializer_class = CompetenciaSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Permite filtrar competencias por activa y en_curso
        """
        queryset = super().get_queryset()
        
        # Filtro por activa
        activa = self.request.query_params.get('activa')
        if activa is not None:
            activa_bool = activa.lower() == 'true'
            queryset = queryset.filter(activa=activa_bool)
        
        # Filtro por en_curso
        en_curso = self.request.query_params.get('en_curso')
        if en_curso is not None:
            en_curso_bool = en_curso.lower() == 'true'
            queryset = queryset.filter(en_curso=en_curso_bool)
        
        return queryset


class EquipoViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para Equipos (solo lectura)
    
    Endpoints automáticos:
    - GET /api/equipos/          -> Lista todos los equipos
    - GET /api/equipos/{id}/     -> Detalle de un equipo
    
    Filtros disponibles via query params:
    - ?competencia_id={id}
    - ?juez_id={id}
    """
    queryset = Equipo.objects.select_related(
        'juez_asignado',
        'juez_asignado__competencia'
    ).all().order_by('dorsal')
    serializer_class = EquipoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Permite filtrar equipos por competencia_id y juez_id
        """
        queryset = super().get_queryset()
        
        # Filtro por competencia
        competencia_id = self.request.query_params.get('competencia_id')
        if competencia_id:
            queryset = queryset.filter(juez_asignado__competencia_id=competencia_id)
        
        # Filtro por juez
        juez_id = self.request.query_params.get('juez_id')
        if juez_id:
            queryset = queryset.filter(juez_asignado_id=juez_id)
        
        return queryset
