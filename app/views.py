from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import EnvioTiemposSerializer
from .models import Equipo, RegistroTiempo, Juez



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
