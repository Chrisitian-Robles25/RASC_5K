# 🔄 Flujo de Comunicación App Móvil ↔️ Servidor

## 📊 Diagrama Completo

```
┌─────────────────────────────────────────────────────────────────────┐
│                        APP MÓVIL (Flutter/React Native)              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 1. POST /api/login/
                           │    {username, password}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVIDOR DJANGO (API REST)                    │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ LoginView                                                     │   │
│  │ - Valida credenciales del juez                                │   │
│  │ - Genera tokens JWT (access + refresh)                        │   │
│  │ - Retorna datos del juez y competencia                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 2. Respuesta
                           │    {access, refresh, juez{...}}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APP MÓVIL                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Guarda en almacenamiento local:                               │   │
│  │ - access_token                                                │   │
│  │ - refresh_token                                               │   │
│  │ - juez_id                                                     │   │
│  │ - competencia_id                                              │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 3. Conectar WebSocket
                           │    ws://servidor/ws/juez/{id}/?token={access}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVIDOR DAPHNE (WebSocket)                   │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ JuezConsumer.connect()                                        │   │
│  │ 1. Valida token JWT                                           │   │
│  │ 2. Verifica juez activo                                       │   │
│  │ 3. Verifica competencia asignada                              │   │
│  │ 4. Verifica competencia activa                                │   │
│  │ 5. Acepta conexión                                            │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 4. Mensaje de conexión
                           │    {tipo: 'conexion_establecida', competencia: {...}}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APP MÓVIL                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Actualiza UI:                                                 │   │
│  │ - Estado: Conectado ✅                                        │   │
│  │ - Competencia: {nombre}                                       │   │
│  │ - En curso: true/false                                        │   │
│  │ - Habilita/deshabilita botones según en_curso                 │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 5. JUEZ PRESIONA "REGISTRAR TIEMPO"
                           │    (15 veces o más)
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APP MÓVIL                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ Por cada registro:                                            │   │
│  │ 1. Captura timestamp: DateTime.now()                          │   │
│  │ 2. Agrega a array local                                       │   │
│  │ 3. Actualiza UI (contador: 1/15, 2/15, ...)                  │   │
│  │                                                               │   │
│  │ Cuando llega a 15:                                            │   │
│  │ 4. Construye mensaje JSON batch                               │   │
│  │ 5. Envía por WebSocket                                        │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 6. Envío por WebSocket
                           │    {tipo: 'registrar_tiempos', equipo_id: 1, registros: [...]}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        SERVIDOR (WebSocket Consumer)                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ JuezConsumer.receive_json()                                   │   │
│  │ 1. Identifica tipo: 'registrar_tiempos'                       │   │
│  │ 2. Llama a manejar_registro_tiempos_batch()                   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ manejar_registro_tiempos_batch()                              │   │
│  │                                                               │   │
│  │ VALIDACIONES:                                                 │   │
│  │ ✅ equipo_id presente                                         │   │
│  │ ✅ registros es un array                                      │   │
│  │ ✅ máximo 15 registros                                        │   │
│  │                                                               │   │
│  │ PROCESAMIENTO:                                                │   │
│  │ for cada registro en registros:                               │   │
│  │   ├─ Extrae: tiempo, horas, minutos, segundos, ms            │   │
│  │   ├─ Llama: guardar_registro_tiempo()                        │   │
│  │   │   ├─ Verifica competencia.en_curso = True                │   │
│  │   │   ├─ Verifica juez tiene permiso para equipo             │   │
│  │   │   ├─ Crea RegistroTiempo en DB                           │   │
│  │   │   └─ Retorna ID o error                                  │   │
│  │   ├─ Si éxito: agrega a registros_guardados                  │   │
│  │   └─ Si falla: agrega a registros_fallidos                   │   │
│  │                                                               │   │
│  │ RESPUESTA:                                                    │   │
│  │ Envía resumen con totales y detalles                          │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────────────┘
                           │
                           │ 7. Respuesta del servidor
                           │    {tipo: 'tiempos_registrados_batch',
                           │     total_guardados: 14, total_fallidos: 1, ...}
                           ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        APP MÓVIL                                     │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │ onMessage(data)                                               │   │
│  │                                                               │   │
│  │ switch(data.tipo):                                            │   │
│  │   case 'tiempos_registrados_batch':                           │   │
│  │     ├─ Muestra notificación: "14 guardados, 1 fallido"       │   │
│  │     ├─ Limpia array local de tiempos                         │   │
│  │     ├─ Actualiza contador a 0/15                             │   │
│  │     └─ Si hay fallidos, muestra detalles                     │   │
│  └──────────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 🎬 Escenarios Especiales

### Escenario 1: Competencia se Inicia Durante Conexión

```
APP (conectada, competencia detenida)
  │
  │ Usuario NO puede registrar tiempos (botones deshabilitados)
  │
  ▼
ADMIN inicia competencia
  │
  ├─► DB: competencia.en_curso = True
  │
  ├─► Envía notificación WebSocket a todos los jueces conectados
  │
  ▼
APP recibe mensaje
  │
  │ {tipo: 'competencia_iniciada', competencia_id: 1}
  │
  ├─► Actualiza estado local: en_curso = true
  ├─► Habilita botones de registro
  └─► Muestra notificación: "🚀 Competencia iniciada"
```

### Escenario 2: Competencia se Detiene Durante Registro

```
APP (registrando tiempos)
  │
  │ Tiene 8 tiempos en memoria (8/15)
  │
  ▼
ADMIN detiene competencia
  │
  ├─► DB: competencia.en_curso = False
  │
  ├─► Envía notificación WebSocket a todos los jueces
  │
  ▼
APP recibe mensaje
  │
  │ {tipo: 'competencia_detenida', competencia_id: 1}
  │
  ├─► Actualiza estado: en_curso = false
  ├─► Deshabilita botones de registro
  ├─► Muestra notificación: "🛑 Competencia detenida"
  └─► DECISIÓN: ¿Mantener tiempos en memoria o descartarlos?
      │
      ├─► Opción A: Mantenerlos (permitir envío manual posterior)
      └─► Opción B: Descartarlos (mayor seguridad)
```

### Escenario 3: Pérdida de Conexión

```
APP (registrando tiempos)
  │
  │ Tiene 12 tiempos en memoria (12/15)
  │
  ▼
WebSocket se desconecta (red móvil inestable)
  │
  ├─► onDisconnected() se ejecuta
  │
  ├─► Muestra alerta: "❌ Conexión perdida"
  │
  ├─► Deshabilita botones de registro
  │
  └─► DECISIÓN APP:
      │
      ├─► Opción A: Intentar reconexión automática
      │     ├─ setInterval cada 5 segundos
      │     └─ Reenviar tiempos pendientes al reconectar
      │
      └─► Opción B: Esperar reconexión manual del usuario
            └─ Mantener tiempos en memoria hasta reconectar
```

### Escenario 4: Token Expira Durante Uso

```
APP (conectada, token expirando)
  │
  │ access_token válido por 1 hora
  │ Pasaron 58 minutos desde login
  │
  ▼
APP intenta registrar tiempos
  │
  ├─► Envía mensaje WebSocket
  │
  ▼
SERVIDOR valida token
  │
  ├─► Token expirado
  │
  └─► Cierra conexión WebSocket
      │
      ▼
APP detecta desconexión
  │
  ├─► onDisconnected() se ejecuta
  │
  ├─► Intenta refresh_token
  │     │
  │     ├─► POST /api/token/refresh/
  │     │     {refresh: "eyJh..."}
  │     │
  │     └─► Recibe nuevo access_token
  │
  ├─► Reconecta WebSocket con nuevo token
  │
  └─► Reenvía tiempos pendientes
```

---

## 🔄 Diagrama de Estados de la App

```
┌────────────────────────────────────────────────────────────────┐
│                                                                 │
│   [INICIO] ──► [LOGIN] ──► [CONECTANDO] ──► [CONECTADO]        │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         [COMPETENCIA          │
│      │            │             │          DETENIDA]            │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         (recibe inicio)       │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         [COMPETENCIA          │
│      │            │             │          EN CURSO]            │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         [REGISTRANDO]         │
│      │            │             │         (0/15, 1/15...)       │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         [ENVIANDO]            │
│      │            │             │         (15/15)               │
│      │            │             │                 │             │
│      │            │             │                 ▼             │
│      │            │             │         [CONFIRMADO]          │
│      │            │             │                 │             │
│      │            │             │                 └─────┐       │
│      │            │             │                       │       │
│      │            │             └───[ERROR]◄────────────┘       │
│      │            │                     │                       │
│      │            └───[ERROR LOGIN]     │                       │
│      │                                  │                       │
│      └──────[LOGOUT]◄───────────────────┘                       │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## 📱 Resumen del Flujo para Desarrolladores

### 1️⃣ Inicialización (Una vez)

```dart
// Al abrir la app
1. Verificar si hay sesión guardada (access_token existe)
2. Si no hay sesión → Pantalla de Login
3. Si hay sesión → Intentar conectar WebSocket
```

### 2️⃣ Login

```dart
// Usuario ingresa credenciales
1. POST /api/login/ con {username, password}
2. Guardar {access, refresh, juez_id} en almacenamiento seguro
3. Conectar WebSocket automáticamente
```

### 3️⃣ WebSocket Persistente

```dart
// Mantener conexión abierta mientras app está activa
1. Conectar: ws://servidor/ws/juez/{id}/?token={access}
2. Escuchar mensajes continuamente
3. Actualizar UI según mensajes recibidos
4. Reconectar si se pierde conexión
```

### 4️⃣ Registro de Tiempos

```dart
// Usuario presiona botón de registro
1. Capturar timestamp actual
2. Agregar a array local: tiempos.add({tiempo, horas, minutos...})
3. Actualizar contador en UI: "12/15"
4. Si length == 15:
   - Enviar por WebSocket: {tipo: 'registrar_tiempos', registros: [...]}
   - Esperar confirmación
   - Limpiar array local
```

### 5️⃣ Manejo de Eventos

```dart
onMessage(data) {
  switch(data.tipo) {
    case 'conexion_establecida':
      // Actualizar estado de competencia
      break;

    case 'competencia_iniciada':
      // Habilitar botones de registro
      break;

    case 'competencia_detenida':
      // Deshabilitar botones de registro
      break;

    case 'tiempos_registrados_batch':
      // Mostrar confirmación
      // Limpiar array local
      break;

    case 'error':
      // Mostrar error al usuario
      break;
  }
}
```

---

## ✅ Checklist de Implementación

-   [ ] Login guarda tokens de forma segura
-   [ ] WebSocket se conecta al login exitoso
-   [ ] UI muestra estado de conexión (conectado/desconectado)
-   [ ] UI muestra estado de competencia (en curso/detenida)
-   [ ] Botones se habilitan/deshabilitan según competencia
-   [ ] Se capturan tiempos con timestamp preciso
-   [ ] Se muestra contador de tiempos (X/15)
-   [ ] Se envían tiempos cuando se llega a 15
-   [ ] Se maneja respuesta del servidor (éxito/error)
-   [ ] Se limpian tiempos después de envío exitoso
-   [ ] Se manejan todos los tipos de mensajes WebSocket
-   [ ] Se implementa reconexión automática
-   [ ] Se refresca token antes de expirar
-   [ ] Se cierra WebSocket al hacer logout

---

**Para más detalles, consulta:**

-   [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Código completo
-   [API_DOCUMENTACION.md](API_DOCUMENTACION.md) - Documentación de API
-   [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Guía rápida

---

**Última actualización:** 12 de noviembre de 2025
