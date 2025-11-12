import urllib.parse
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


@database_sync_to_async
def get_juez_from_token(token):
    """
    Valida el token JWT y retorna el juez.
    """
    from rest_framework_simplejwt.tokens import AccessToken
    from .models import Juez
    
    try:
        # Validar el token
        access_token = AccessToken(token)
        juez_id = access_token.get('juez_id')
        
        if not juez_id:
            return None
        
        # Obtener el juez
        juez = Juez.objects.get(id=juez_id, activo=True)
        return juez
    except Exception:
        return None


class JuezConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        # Expect token in querystring: ?token=...
        qs = self.scope.get('query_string', b'').decode()
        params = urllib.parse.parse_qs(qs)
        token = params.get('token', [None])[0]
        if not token:
            await self.close()
            return

        try:
            juez = await get_juez_from_token(token)
            if not juez:
                await self.close()
                return
        except Exception:
            await self.close()
            return

        self.juez = juez

        # Verificar que el juez_id de la URL coincida con el juez autenticado
        self.juez_id = str(self.scope['url_route']['kwargs'].get('juez_id'))
        if str(self.juez.id) != self.juez_id:
            await self.close()
            return

        self.group_name = f'juez_{self.juez_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        try:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        except Exception:
            pass

    async def receive_json(self, content, **kwargs):
        """
        Maneja mensajes JSON del cliente.
        
        Mensajes soportados:
        1. registrar_tiempo: Registra el tiempo de llegada de un equipo
        """
        tipo = content.get('tipo')
        
        if tipo == 'registrar_tiempo':
            await self.manejar_registro_tiempo(content)
        else:
            # Mensaje no reconocido
            await self.send_json({
                'tipo': 'error',
                'mensaje': f'Tipo de mensaje no reconocido: {tipo}'
            })
    
    async def manejar_registro_tiempo(self, content):
        """
        Registra el tiempo de un equipo.
        
        Esperado en content:
        {
            "tipo": "registrar_tiempo",
            "equipo_id": 1,
            "tiempo": 1234567,  # milisegundos totales
            "horas": 0,
            "minutos": 20,
            "segundos": 34,
            "milisegundos": 567
        }
        """
        try:
            equipo_id = content.get('equipo_id')
            tiempo = content.get('tiempo')
            horas = content.get('horas', 0)
            minutos = content.get('minutos', 0)
            segundos = content.get('segundos', 0)
            milisegundos = content.get('milisegundos', 0)
            
            # Validar que se enviaron todos los datos
            if equipo_id is None or tiempo is None:
                await self.send_json({
                    'tipo': 'error',
                    'mensaje': 'Faltan datos requeridos: equipo_id y tiempo son obligatorios'
                })
                return
            
            # Registrar el tiempo en la base de datos
            registro = await self.guardar_registro_tiempo(
                equipo_id=equipo_id,
                tiempo=tiempo,
                horas=horas,
                minutos=minutos,
                segundos=segundos,
                milisegundos=milisegundos
            )
            
            if registro:
                # Enviar confirmación al cliente
                await self.send_json({
                    'tipo': 'tiempo_registrado',
                    'registro': {
                        'id_registro': str(registro.id_registro),
                        'equipo_id': registro.equipo_id,
                        'equipo_nombre': registro.equipo.nombre,
                        'equipo_dorsal': registro.equipo.dorsal,
                        'tiempo': registro.tiempo,
                        'horas': registro.horas,
                        'minutos': registro.minutos,
                        'segundos': registro.segundos,
                        'milisegundos': registro.milisegundos,
                        'timestamp': registro.timestamp.isoformat()
                    }
                })
            
        except Exception as e:
            await self.send_json({
                'tipo': 'error',
                'mensaje': f'Error al registrar tiempo: {str(e)}'
            })
    
    @database_sync_to_async
    def guardar_registro_tiempo(self, equipo_id, tiempo, horas, minutos, segundos, milisegundos):
        """
        Guarda el registro de tiempo en la base de datos.
        Valida que el equipo pertenezca al juez autenticado.
        """
        from .models import Equipo, RegistroTiempo
        
        try:
            # Verificar que el equipo existe
            equipo = Equipo.objects.get(id=equipo_id)
            
            # Verificar que el equipo pertenece a este juez
            if equipo.juez_asignado_id != self.juez.id:
                raise ValueError(
                    f'El equipo con ID {equipo_id} no pertenece a tu lista de equipos asignados'
                )
            
            # Crear el registro de tiempo
            registro = RegistroTiempo.objects.create(
                equipo=equipo,
                tiempo=tiempo,
                horas=horas,
                minutos=minutos,
                segundos=segundos,
                milisegundos=milisegundos
            )
            
            return registro
            
        except Equipo.DoesNotExist:
            raise ValueError(f'El equipo con ID {equipo_id} no existe')
        except Exception as e:
            raise Exception(f'Error al guardar registro: {str(e)}')

    async def carrera_iniciada(self, event):
        await self.send_json({
            'type': 'carrera.iniciada',
            'data': event.get('data', {})
        })
