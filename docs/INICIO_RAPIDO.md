# 🚀 Inicio Rápido - API de Registro de Tiempos

## 📋 Resumen

**URL Base:** `http://tu-servidor.com`  
**WebSocket:** `ws://tu-servidor.com`

---

## 🔐 Autenticación (3 pasos)

### 1. Login

```bash
POST /api/login/
Content-Type: application/json

{
  "username": "juez1",
  "password": "password123"
}
```

**Respuesta:**

```json
{
    "access": "eyJhbGc...",
    "refresh": "eyJhbGc...",
    "juez": {
        "id": 1,
        "username": "juez1",
        "competencia": {
            "id": 1,
            "nombre": "Carrera 5K",
            "en_curso": true
        }
    }
}
```

### 2. Conectar WebSocket

```javascript
const ws = new WebSocket(
    `ws://tu-servidor.com/ws/juez/${juez_id}/?token=${access_token}`
);
```

### 3. Enviar Tiempos (Batch)

```javascript
const mensaje = {
    tipo: "registrar_tiempos",
    equipo_id: 1,
    registros: [
        { tiempo: 900000, horas: 0, minutos: 15, segundos: 0, milisegundos: 0 },
        {
            tiempo: 950000,
            horas: 0,
            minutos: 15,
            segundos: 50,
            milisegundos: 0,
        },
        // ... hasta 15 registros
    ],
};

ws.send(JSON.stringify(mensaje));
```

---

## 📱 Ejemplo Flutter Completo

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';

// 1. LOGIN
final loginResponse = await http.post(
  Uri.parse('http://tu-servidor.com/api/login/'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({'username': 'juez1', 'password': 'password123'}),
);

final loginData = jsonDecode(loginResponse.body);
final accessToken = loginData['access'];
final juezId = loginData['juez']['id'];

// 2. CONECTAR WEBSOCKET
final channel = WebSocketChannel.connect(
  Uri.parse('ws://tu-servidor.com/ws/juez/$juezId/?token=$accessToken')
);

channel.stream.listen((message) {
  final data = jsonDecode(message);
  print('Mensaje: ${data['tipo']}');
});

// 3. ENVIAR TIEMPOS
final mensaje = {
  'tipo': 'registrar_tiempos',
  'equipo_id': 1,
  'registros': [
    {'tiempo': 900000, 'horas': 0, 'minutos': 15, 'segundos': 0, 'milisegundos': 0},
    {'tiempo': 950000, 'horas': 0, 'minutos': 15, 'segundos': 50, 'milisegundos': 0},
    // ... más tiempos
  ],
};

channel.sink.add(jsonEncode(mensaje));
```

---

## 🔌 Mensajes WebSocket

### Enviar (Cliente → Servidor)

#### Registro Individual

```json
{
    "tipo": "registrar_tiempo",
    "equipo_id": 1,
    "tiempo": 1234567
}
```

#### Registro en Lote (hasta 15)

```json
{
    "tipo": "registrar_tiempos",
    "equipo_id": 1,
    "registros": [
        {
            "tiempo": 900000,
            "horas": 0,
            "minutos": 15,
            "segundos": 0,
            "milisegundos": 0
        }
        // ... más registros
    ]
}
```

### Recibir (Servidor → Cliente)

#### Conexión Establecida

```json
{
    "tipo": "conexion_establecida",
    "mensaje": "Conectado exitosamente",
    "competencia": {
        "id": 1,
        "nombre": "Carrera 5K",
        "en_curso": true
    }
}
```

#### Tiempos Registrados

```json
{
  "tipo": "tiempos_registrados_batch",
  "equipo_id": 1,
  "total_enviados": 15,
  "total_guardados": 14,
  "total_fallidos": 1,
  "registros_guardados": [...],
  "registros_fallidos": [...]
}
```

#### Competencia Iniciada/Detenida

```json
{
    "tipo": "competencia_iniciada",
    "mensaje": "La competencia ha iniciado"
}
```

```json
{
    "tipo": "competencia_detenida",
    "mensaje": "La competencia ha sido detenida"
}
```

#### Error

```json
{
    "tipo": "error",
    "mensaje": "La competencia no está en curso"
}
```

---

## 📊 Endpoints HTTP/REST

| Método | Endpoint              | Descripción     |
| ------ | --------------------- | --------------- |
| POST   | `/api/login/`         | Autenticación   |
| POST   | `/api/logout/`        | Cerrar sesión   |
| POST   | `/api/token/refresh/` | Refrescar token |

---

## ⏱️ Duración de Tokens

-   **Access Token:** 1 hora
-   **Refresh Token:** 7 días

---

## ✅ Validaciones

1. Token JWT válido
2. Juez activo
3. Competencia asignada y activa
4. **Competencia EN CURSO** para registrar tiempos
5. Máximo 15 registros por lote

---

## 🔍 Códigos de Error Comunes

| Código | Mensaje                 | Solución                     |
| ------ | ----------------------- | ---------------------------- |
| 401    | Credenciales inválidas  | Verificar usuario/contraseña |
| 401    | Token expirado          | Refrescar token              |
| 403    | Usuario inactivo        | Contactar administrador      |
| 400    | Máximo 15 registros     | Dividir en lotes             |
| error  | Competencia no en curso | Esperar a que inicie         |

---

## 📚 Documentación Completa

Para más detalles, consulta:

-   **[API_DOCUMENTACION.md](API_DOCUMENTACION.md)** - Documentación completa de todos los endpoints
-   **[REGISTRO_BATCH.md](REGISTRO_BATCH.md)** - Guía detallada de registro en lote
-   **[WEBSOCKET_SIMPLE.md](WEBSOCKET_SIMPLE.md)** - Guía simple de WebSocket

---

## 🧪 Probar la API

1. **Login:**

    ```bash
    curl -X POST http://127.0.0.1:8000/api/login/ \
      -H "Content-Type: application/json" \
      -d '{"username":"juez1","password":"password123"}'
    ```

2. **WebSocket:** Abrir `test_registro_batch.html` en el navegador

---

## 💡 Tips

-   ✅ Guardar tokens en almacenamiento seguro (SharedPreferences, AsyncStorage)
-   ✅ Implementar reconexión automática de WebSocket
-   ✅ Refrescar token automáticamente antes de que expire
-   ✅ Manejar estado de competencia (en_curso) en la UI
-   ✅ Validar tiempos antes de enviar

---

**Última actualización:** 12 de noviembre de 2025
