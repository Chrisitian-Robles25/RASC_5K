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
        # Optionally handle messages from client
        # For now, ignore or echo
        await self.send_json({'received': content})

    async def carrera_iniciada(self, event):
        await self.send_json({
            'type': 'carrera.iniciada',
            'data': event.get('data', {})
        })
