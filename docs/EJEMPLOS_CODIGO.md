jhhgr# 💻 Ejemplos de Código Completos

Esta guía contiene ejemplos funcionales completos para integrar la API en diferentes plataformas.

---

## 📱 Flutter (Dart)

### Servicio Completo de Autenticación y WebSocket

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TiemposApiService {
  static const String baseUrl = 'http://tu-servidor.com';
  static const String wsUrl = 'ws://tu-servidor.com';

  WebSocketChannel? _channel;
  Function(Map<String, dynamic>)? onMessage;
  Function()? onConnected;
  Function()? onDisconnected;

  // ============================================
  // AUTENTICACIÓN
  // ============================================

  /// Login del juez
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/api/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // Guardar en SharedPreferences
        final prefs = await SharedPreferences.getInstance();
        await prefs.setString('access_token', data['access']);
        await prefs.setString('refresh_token', data['refresh']);
        await prefs.setInt('juez_id', data['juez']['id']);
        await prefs.setString('juez_username', data['juez']['username']);

        return data;
      } else {
        final error = jsonDecode(response.body);
        throw Exception(error['error'] ?? 'Error en login');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  /// Logout del juez
  Future<void> logout() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accessToken = prefs.getString('access_token');
      final refreshToken = prefs.getString('refresh_token');

      if (accessToken != null && refreshToken != null) {
        await http.post(
          Uri.parse('$baseUrl/api/logout/'),
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $accessToken',
          },
          body: jsonEncode({'refresh': refreshToken}),
        );
      }

      // Cerrar WebSocket
      await desconectarWebSocket();

      // Limpiar tokens
      await prefs.clear();

    } catch (e) {
      print('Error en logout: $e');
      // Limpiar de todas formas
      final prefs = await SharedPreferences.getInstance();
      await prefs.clear();
    }
  }

  /// Refrescar access token
  Future<String> refreshAccessToken() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final refreshToken = prefs.getString('refresh_token');

      if (refreshToken == null) {
        throw Exception('No hay refresh token');
      }

      final response = await http.post(
        Uri.parse('$baseUrl/api/token/refresh/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'refresh': refreshToken}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final newAccessToken = data['access'];

        // Guardar nuevo access token
        await prefs.setString('access_token', newAccessToken);

        return newAccessToken;
      } else {
        throw Exception('Token expirado');
      }
    } catch (e) {
      throw Exception('Error al refrescar token: $e');
    }
  }

  // ============================================
  // WEBSOCKET
  // ============================================

  /// Conectar al WebSocket
  Future<void> conectarWebSocket() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final accessToken = prefs.getString('access_token');
      final juezId = prefs.getInt('juez_id');

      if (accessToken == null || juezId == null) {
        throw Exception('No hay sesión activa');
      }

      final uri = Uri.parse('$wsUrl/ws/juez/$juezId/?token=$accessToken');
      _channel = WebSocketChannel.connect(uri);

      print('🔌 Conectando WebSocket...');

      _channel!.stream.listen(
        (message) {
          final data = jsonDecode(message);
          print('📨 Mensaje recibido: ${data['tipo']}');

          if (data['tipo'] == 'conexion_establecida') {
            print('✅ WebSocket conectado');
            onConnected?.call();
          }

          onMessage?.call(data);
        },
        onError: (error) {
          print('❌ Error en WebSocket: $error');
        },
        onDone: () {
          print('🔌 WebSocket desconectado');
          onDisconnected?.call();
        },
      );

    } catch (e) {
      throw Exception('Error al conectar WebSocket: $e');
    }
  }

  /// Desconectar WebSocket
  Future<void> desconectarWebSocket() async {
    await _channel?.sink.close();
    _channel = null;
  }

  /// Enviar mensaje por WebSocket
  void _enviarMensaje(Map<String, dynamic> mensaje) {
    if (_channel == null) {
      throw Exception('WebSocket no conectado');
    }

    _channel!.sink.add(jsonEncode(mensaje));
    print('📤 Mensaje enviado: ${mensaje['tipo']}');
  }

  // ============================================
  // REGISTRO DE TIEMPOS
  // ============================================

  /// Registrar un solo tiempo
  void registrarTiempo(int equipoId, int tiempo) {
    _enviarMensaje({
      'tipo': 'registrar_tiempo',
      'equipo_id': equipoId,
      'tiempo': tiempo,
    });
  }

  /// Registrar múltiples tiempos (batch)
  void registrarTiemposLote(int equipoId, List<Map<String, dynamic>> registros) {
    if (registros.isEmpty) {
      throw Exception('La lista de registros está vacía');
    }

    if (registros.length > 15) {
      throw Exception('Máximo 15 registros por lote');
    }

    _enviarMensaje({
      'tipo': 'registrar_tiempos',
      'equipo_id': equipoId,
      'registros': registros,
    });
  }

  // ============================================
  // HELPERS
  // ============================================

  /// Verificar si hay sesión activa
  Future<bool> haySesionActiva() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString('access_token') != null;
  }

  /// Obtener datos del juez
  Future<Map<String, dynamic>?> obtenerDatosJuez() async {
    final prefs = await SharedPreferences.getInstance();
    final juezId = prefs.getInt('juez_id');
    final username = prefs.getString('juez_username');

    if (juezId == null) return null;

    return {
      'id': juezId,
      'username': username,
    };
  }
}
```

### Widget de Ejemplo: Pantalla de Registro

```dart
import 'package:flutter/material.dart';

class RegistroTiemposScreen extends StatefulWidget {
  @override
  _RegistroTiemposScreenState createState() => _RegistroTiemposScreenState();
}

class _RegistroTiemposScreenState extends State<RegistroTiemposScreen> {
  final TiemposApiService _apiService = TiemposApiService();

  bool _conectado = false;
  bool _competenciaEnCurso = false;
  int _equipoIdActual = 1;
  List<Map<String, dynamic>> _tiemposRegistrados = [];
  String _mensajeEstado = 'Desconectado';

  @override
  void initState() {
    super.initState();
    _inicializar();
  }

  Future<void> _inicializar() async {
    // Configurar callbacks
    _apiService.onConnected = () {
      setState(() {
        _conectado = true;
        _mensajeEstado = 'Conectado';
      });
    };

    _apiService.onDisconnected = () {
      setState(() {
        _conectado = false;
        _mensajeEstado = 'Desconectado';
      });
    };

    _apiService.onMessage = (data) {
      _manejarMensaje(data);
    };

    // Conectar
    try {
      await _apiService.conectarWebSocket();
    } catch (e) {
      _mostrarError('Error al conectar: $e');
    }
  }

  void _manejarMensaje(Map<String, dynamic> data) {
    switch (data['tipo']) {
      case 'conexion_establecida':
        setState(() {
          _competenciaEnCurso = data['competencia']['en_curso'] ?? false;
        });
        break;

      case 'competencia_iniciada':
        setState(() {
          _competenciaEnCurso = true;
          _mensajeEstado = '🚀 Competencia iniciada';
        });
        _mostrarSnackbar('Competencia iniciada', Colors.green);
        break;

      case 'competencia_detenida':
        setState(() {
          _competenciaEnCurso = false;
          _mensajeEstado = '🛑 Competencia detenida';
        });
        _mostrarSnackbar('Competencia detenida', Colors.orange);
        break;

      case 'tiempos_registrados_batch':
        final guardados = data['total_guardados'];
        final fallidos = data['total_fallidos'];

        _mostrarSnackbar(
          '$guardados registrados, $fallidos fallidos',
          fallidos > 0 ? Colors.orange : Colors.green,
        );

        setState(() {
          _tiemposRegistrados.clear();
        });
        break;

      case 'error':
        _mostrarError(data['mensaje']);
        break;
    }
  }

  void _registrarTiempo() {
    final ahora = DateTime.now();

    final registro = {
      'tiempo': ahora.millisecondsSinceEpoch,
      'horas': ahora.hour,
      'minutos': ahora.minute,
      'segundos': ahora.second,
      'milisegundos': ahora.millisecond,
    };

    setState(() {
      _tiemposRegistrados.add(registro);
    });

    // Enviar automáticamente si llegamos a 15
    if (_tiemposRegistrados.length >= 15) {
      _enviarTiempos();
    }
  }

  void _enviarTiempos() {
    if (_tiemposRegistrados.isEmpty) {
      _mostrarError('No hay tiempos para enviar');
      return;
    }

    try {
      _apiService.registrarTiemposLote(_equipoIdActual, _tiemposRegistrados);
      _mostrarSnackbar('Enviando ${_tiemposRegistrados.length} tiempos...', Colors.blue);
    } catch (e) {
      _mostrarError('Error al enviar: $e');
    }
  }

  void _mostrarSnackbar(String mensaje, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(mensaje),
        backgroundColor: color,
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _mostrarError(String mensaje) {
    _mostrarSnackbar(mensaje, Colors.red);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Registro de Tiempos'),
        backgroundColor: _competenciaEnCurso ? Colors.green : Colors.red,
      ),
      body: Column(
        children: [
          // Estado
          Container(
            width: double.infinity,
            padding: EdgeInsets.all(16),
            color: _conectado ? Colors.green[100] : Colors.red[100],
            child: Column(
              children: [
                Text(
                  _mensajeEstado,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 8),
                Text(
                  _competenciaEnCurso ? 'EN CURSO' : 'DETENIDA',
                  style: TextStyle(fontSize: 16),
                ),
              ],
            ),
          ),

          // Botón de registro
          Padding(
            padding: EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _competenciaEnCurso ? _registrarTiempo : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue,
                minimumSize: Size(double.infinity, 60),
              ),
              child: Text(
                '⏱️ REGISTRAR TIEMPO',
                style: TextStyle(fontSize: 20, color: Colors.white),
              ),
            ),
          ),

          // Contador
          Text(
            'Tiempos registrados: ${_tiemposRegistrados.length}/15',
            style: TextStyle(fontSize: 16),
          ),

          // Lista de tiempos
          Expanded(
            child: ListView.builder(
              itemCount: _tiemposRegistrados.length,
              itemBuilder: (context, index) {
                final tiempo = _tiemposRegistrados[index];
                return ListTile(
                  leading: CircleAvatar(child: Text('${index + 1}')),
                  title: Text('Corredor ${index + 1}'),
                  subtitle: Text(
                    '${tiempo['horas']}:${tiempo['minutos']}:${tiempo['segundos']}.${tiempo['milisegundos']}'
                  ),
                );
              },
            ),
          ),

          // Botón de envío
          Padding(
            padding: EdgeInsets.all(16),
            child: ElevatedButton(
              onPressed: _tiemposRegistrados.isNotEmpty ? _enviarTiempos : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.orange,
                minimumSize: Size(double.infinity, 50),
              ),
              child: Text(
                '📤 ENVIAR ${_tiemposRegistrados.length} TIEMPOS',
                style: TextStyle(fontSize: 18, color: Colors.white),
              ),
            ),
          ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _apiService.desconectarWebSocket();
    super.dispose();
  }
}
```

---

## 🌐 JavaScript/TypeScript (React Native / Web)

### Servicio Completo

```typescript
import AsyncStorage from "@react-native-async-storage/async-storage";

interface LoginResponse {
    access: string;
    refresh: string;
    juez: {
        id: number;
        username: string;
        competencia: {
            id: number;
            nombre: string;
            en_curso: boolean;
        };
    };
}

class TiemposApiService {
    private baseUrl = "http://tu-servidor.com";
    private wsUrl = "ws://tu-servidor.com";
    private ws: WebSocket | null = null;

    // Callbacks
    public onMessage?: (data: any) => void;
    public onConnected?: () => void;
    public onDisconnected?: () => void;

    // ============================================
    // AUTENTICACIÓN
    // ============================================

    async login(username: string, password: string): Promise<LoginResponse> {
        try {
            const response = await fetch(`${this.baseUrl}/api/login/`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password }),
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || "Error en login");
            }

            const data: LoginResponse = await response.json();

            // Guardar tokens
            await AsyncStorage.setItem("access_token", data.access);
            await AsyncStorage.setItem("refresh_token", data.refresh);
            await AsyncStorage.setItem("juez_id", data.juez.id.toString());

            return data;
        } catch (error) {
            throw new Error(`Error de conexión: ${error}`);
        }
    }

    async logout(): Promise<void> {
        try {
            const accessToken = await AsyncStorage.getItem("access_token");
            const refreshToken = await AsyncStorage.getItem("refresh_token");

            if (accessToken && refreshToken) {
                await fetch(`${this.baseUrl}/api/logout/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${accessToken}`,
                    },
                    body: JSON.stringify({ refresh: refreshToken }),
                });
            }

            // Cerrar WebSocket
            this.desconectarWebSocket();

            // Limpiar tokens
            await AsyncStorage.clear();
        } catch (error) {
            console.error("Error en logout:", error);
            await AsyncStorage.clear();
        }
    }

    async refreshAccessToken(): Promise<string> {
        const refreshToken = await AsyncStorage.getItem("refresh_token");

        if (!refreshToken) {
            throw new Error("No hay refresh token");
        }

        const response = await fetch(`${this.baseUrl}/api/token/refresh/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (!response.ok) {
            throw new Error("Token expirado");
        }

        const data = await response.json();
        await AsyncStorage.setItem("access_token", data.access);

        return data.access;
    }

    // ============================================
    // WEBSOCKET
    // ============================================

    async conectarWebSocket(): Promise<void> {
        const accessToken = await AsyncStorage.getItem("access_token");
        const juezId = await AsyncStorage.getItem("juez_id");

        if (!accessToken || !juezId) {
            throw new Error("No hay sesión activa");
        }

        const wsUrl = `${this.wsUrl}/ws/juez/${juezId}/?token=${accessToken}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log("✅ WebSocket conectado");
            this.onConnected?.();
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log("📨 Mensaje recibido:", data.tipo);
            this.onMessage?.(data);
        };

        this.ws.onerror = (error) => {
            console.error("❌ Error en WebSocket:", error);
        };

        this.ws.onclose = () => {
            console.log("🔌 WebSocket desconectado");
            this.onDisconnected?.();
        };
    }

    desconectarWebSocket(): void {
        this.ws?.close();
        this.ws = null;
    }

    private enviarMensaje(mensaje: any): void {
        if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
            throw new Error("WebSocket no conectado");
        }

        this.ws.send(JSON.stringify(mensaje));
        console.log("📤 Mensaje enviado:", mensaje.tipo);
    }

    // ============================================
    // REGISTRO DE TIEMPOS
    // ============================================

    registrarTiempo(equipoId: number, tiempo: number): void {
        this.enviarMensaje({
            tipo: "registrar_tiempo",
            equipo_id: equipoId,
            tiempo: tiempo,
        });
    }

    registrarTiemposLote(equipoId: number, registros: any[]): void {
        if (registros.length === 0) {
            throw new Error("La lista de registros está vacía");
        }

        if (registros.length > 15) {
            throw new Error("Máximo 15 registros por lote");
        }

        this.enviarMensaje({
            tipo: "registrar_tiempos",
            equipo_id: equipoId,
            registros: registros,
        });
    }
}

export default new TiemposApiService();
```

---

## 🐍 Python

### Cliente Completo

```python
import asyncio
import json
import requests
import websockets
from typing import Optional, Callable, List, Dict

class TiemposApiService:
    def __init__(self, base_url: str = 'http://tu-servidor.com'):
        self.base_url = base_url
        self.ws_url = base_url.replace('http', 'ws')
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.juez_id: Optional[int] = None
        self.ws: Optional[websockets.WebSocketClientProtocol] = None

        # Callbacks
        self.on_message: Optional[Callable] = None
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None

    # ============================================
    # AUTENTICACIÓN
    # ============================================

    def login(self, username: str, password: str) -> dict:
        """Login del juez"""
        response = requests.post(
            f'{self.base_url}/api/login/',
            json={'username': username, 'password': password}
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access']
            self.refresh_token = data['refresh']
            self.juez_id = data['juez']['id']
            return data
        else:
            error = response.json()
            raise Exception(error.get('error', 'Error en login'))

    def logout(self) -> None:
        """Logout del juez"""
        if self.access_token and self.refresh_token:
            requests.post(
                f'{self.base_url}/api/logout/',
                headers={'Authorization': f'Bearer {self.access_token}'},
                json={'refresh': self.refresh_token}
            )

        self.access_token = None
        self.refresh_token = None
        self.juez_id = None

    def refresh_access_token(self) -> str:
        """Refrescar access token"""
        if not self.refresh_token:
            raise Exception('No hay refresh token')

        response = requests.post(
            f'{self.base_url}/api/token/refresh/',
            json={'refresh': self.refresh_token}
        )

        if response.status_code == 200:
            data = response.json()
            self.access_token = data['access']
            return self.access_token
        else:
            raise Exception('Token expirado')

    # ============================================
    # WEBSOCKET
    # ============================================

    async def conectar_websocket(self):
        """Conectar al WebSocket"""
        if not self.access_token or not self.juez_id:
            raise Exception('No hay sesión activa')

        uri = f'{self.ws_url}/ws/juez/{self.juez_id}/?token={self.access_token}'

        async with websockets.connect(uri) as websocket:
            self.ws = websocket
            print('✅ WebSocket conectado')

            if self.on_connected:
                self.on_connected()

            # Escuchar mensajes
            async for message in websocket:
                data = json.loads(message)
                print(f'📨 Mensaje recibido: {data["tipo"]}')

                if self.on_message:
                    self.on_message(data)

    async def enviar_mensaje(self, mensaje: dict):
        """Enviar mensaje por WebSocket"""
        if not self.ws:
            raise Exception('WebSocket no conectado')

        await self.ws.send(json.dumps(mensaje))
        print(f'📤 Mensaje enviado: {mensaje["tipo"]}')

    # ============================================
    # REGISTRO DE TIEMPOS
    # ============================================

    async def registrar_tiempo(self, equipo_id: int, tiempo: int):
        """Registrar un solo tiempo"""
        await self.enviar_mensaje({
            'tipo': 'registrar_tiempo',
            'equipo_id': equipo_id,
            'tiempo': tiempo,
        })

    async def registrar_tiempos_lote(self, equipo_id: int, registros: List[Dict]):
        """Registrar múltiples tiempos (batch)"""
        if len(registros) == 0:
            raise Exception('La lista de registros está vacía')

        if len(registros) > 15:
            raise Exception('Máximo 15 registros por lote')

        await self.enviar_mensaje({
            'tipo': 'registrar_tiempos',
            'equipo_id': equipo_id,
            'registros': registros,
        })


# Ejemplo de uso
async def main():
    service = TiemposApiService()

    # 1. Login
    login_data = service.login('juez1', 'password123')
    print(f"✅ Login exitoso: {login_data['juez']['username']}")

    # 2. Callbacks
    def on_message(data):
        tipo = data['tipo']
        if tipo == 'tiempos_registrados_batch':
            print(f"✅ {data['total_guardados']} tiempos guardados")

    service.on_message = on_message

    # 3. Conectar WebSocket y enviar tiempos
    async def enviar_tiempos():
        await service.conectar_websocket()

        # Enviar 5 tiempos de ejemplo
        registros = [
            {'tiempo': 900000 + i*1000, 'horas': 0, 'minutos': 15, 'segundos': i, 'milisegundos': 0}
            for i in range(5)
        ]

        await service.registrar_tiempos_lote(1, registros)

    # Ejecutar
    await enviar_tiempos()

if __name__ == '__main__':
    asyncio.run(main())
```

---

## ✅ Checklist de Integración

Antes de poner en producción, verifica:

-   [ ] Login funciona correctamente
-   [ ] Tokens se guardan de forma segura
-   [ ] WebSocket se conecta exitosamente
-   [ ] Se manejan todos los tipos de mensajes
-   [ ] Se valida el estado de la competencia
-   [ ] Se implementa reconexión automática
-   [ ] Se manejan errores de red
-   [ ] Se refresca el token automáticamente
-   [ ] Se limpia sesión al cerrar la app
-   [ ] Se prueba con 15 tiempos simultáneos

---

**Última actualización:** 12 de noviembre de 2025
