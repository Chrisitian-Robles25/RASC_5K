# 📚 Índice de Documentación - Server5K

Bienvenido a la documentación completa del servidor de registro de tiempos para carreras 5K.

---

## 🚀 Rutas Rápidas

### Si quieres explorar la API de forma interactiva:

👉 **[Swagger UI](http://127.0.0.1:8000/api/docs/)** 🔥 - Prueba endpoints en el navegador (¡SIN escribir código!)

### Si eres desarrollador de apps móviles y necesitas integrar el servidor:

👉 **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Comienza aquí en 5 minutos

### Si necesitas entender el flujo completo de comunicación:

👉 **[FLUJO_COMPLETO.md](FLUJO_COMPLETO.md)** - Diagramas visuales del flujo

### Si necesitas ejemplos de código completos:

👉 **[EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md)** - Flutter, React Native, Python

---

## 📖 Documentación Completa

### 1. Guías de Integración

| Documento                                                | Descripción                                      | Para quién                   |
| -------------------------------------------------------- | ------------------------------------------------ | ---------------------------- |
| **[Swagger UI](http://127.0.0.1:8000/api/docs/)** 🔥     | Documentación interactiva (prueba endpoints)     | Todos                        |
| **[SWAGGER_DOCUMENTACION.md](SWAGGER_DOCUMENTACION.md)** | Guía de uso de Swagger/OpenAPI                   | Todos los desarrolladores    |
| **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)**                 | Guía rápida de 5 minutos                         | Todos los desarrolladores    |
| **[FLUJO_COMPLETO.md](FLUJO_COMPLETO.md)**               | Diagramas visuales del flujo completo            | Arquitectos, desarrolladores |
| **[EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md)**             | Código completo en Flutter, React Native, Python | Desarrolladores móviles      |

### 2. Referencia de API

| Documento                                        | Descripción                                          | Para quién                               |
| ------------------------------------------------ | ---------------------------------------------------- | ---------------------------------------- |
| **[API_DOCUMENTACION.md](API_DOCUMENTACION.md)** | Documentación completa de endpoints REST y WebSocket | Todos los desarrolladores                |
| **[REGISTRO_BATCH.md](REGISTRO_BATCH.md)**       | Guía detallada del registro en lote (15 tiempos)     | Desarrolladores que implementan registro |

### 3. Guías Técnicas

| Documento                                                  | Descripción                            | Para quién                                   |
| ---------------------------------------------------------- | -------------------------------------- | -------------------------------------------- |
| **[WEBSOCKET_SIMPLE.md](WEBSOCKET_SIMPLE.md)**             | Tutorial paso a paso de WebSocket      | Principiantes en WebSocket                   |
| **[VALIDACION_COMPETENCIA.md](VALIDACION_COMPETENCIA.md)** | Validación de competencia en curso     | Desarrolladores que implementan validaciones |
| **[README_WEBSOCKET.md](../README_WEBSOCKET.md)**          | Guía completa de WebSocket (detallada) | Desarrolladores avanzados                    |

---

## 🎯 Por Caso de Uso

### Quiero implementar login en mi app móvil

1. Lee: [INICIO_RAPIDO.md](INICIO_RAPIDO.md) - Sección "Autenticación"
2. Copia código: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Sección "Login"
3. Referencia: [API_DOCUMENTACION.md](API_DOCUMENTACION.md) - "POST /api/login/"

### Quiero conectar mi app al WebSocket

1. Lee: [WEBSOCKET_SIMPLE.md](WEBSOCKET_SIMPLE.md) - Tutorial completo
2. Ve diagrama: [FLUJO_COMPLETO.md](FLUJO_COMPLETO.md) - Sección "Diagrama Completo"
3. Copia código: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Sección "WebSocket"

### Quiero enviar 15 tiempos de un equipo

1. Lee: [REGISTRO_BATCH.md](REGISTRO_BATCH.md) - Guía completa
2. Ve ejemplo: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Método `registrarTiemposLote()`
3. Prueba: Abre `test_registro_batch.html` en navegador

### Quiero manejar el estado de la competencia

1. Lee: [VALIDACION_COMPETENCIA.md](VALIDACION_COMPETENCIA.md)
2. Ve diagrama: [FLUJO_COMPLETO.md](FLUJO_COMPLETO.md) - "Escenario 1: Competencia se Inicia"
3. Implementa eventos: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Callbacks

### Quiero manejar errores y reconexión

1. Lee: [FLUJO_COMPLETO.md](FLUJO_COMPLETO.md) - "Escenario 3: Pérdida de Conexión"
2. Implementa: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - Manejo de errores
3. Referencia: [API_DOCUMENTACION.md](API_DOCUMENTACION.md) - Sección "Errores"

---

## 🧪 Archivos de Prueba

Ubicados en la raíz del proyecto:

| Archivo                            | Descripción                             |
| ---------------------------------- | --------------------------------------- |
| `test_registro_batch.html`         | Prueba de envío de 15 registros en lote |
| `test_validacion_competencia.html` | Prueba de validación de competencia     |
| `ejemplo_websocket.html`           | Demo básica de WebSocket                |

**Cómo usar:**

1. Asegúrate de que el servidor esté corriendo: `uv run daphne -b 127.0.0.1 -p 8000 server.asgi:application`
2. Abre el archivo HTML en tu navegador
3. Inicia sesión con: `roryflowers` / `teclado12`

---

## 📋 Endpoints Disponibles

### API REST (HTTP)

| Endpoint              | Método | Descripción            |
| --------------------- | ------ | ---------------------- |
| `/api/login/`         | POST   | Autenticación de juez  |
| `/api/logout/`        | POST   | Cerrar sesión          |
| `/api/token/refresh/` | POST   | Refrescar access token |

### WebSocket

| URL                                                     | Descripción                                 |
| ------------------------------------------------------- | ------------------------------------------- |
| `ws://servidor/ws/juez/{juez_id}/?token={access_token}` | Conexión WebSocket para registro de tiempos |

### Tipos de Mensajes WebSocket

**Enviar (Cliente → Servidor):**

-   `registrar_tiempo` - Registro individual
-   `registrar_tiempos` - Registro en lote (hasta 15)

**Recibir (Servidor → Cliente):**

-   `conexion_establecida` - Conexión exitosa
-   `tiempo_registrado` - Confirmación de registro individual
-   `tiempos_registrados_batch` - Confirmación de registro en lote
-   `competencia_iniciada` - Competencia iniciada
-   `competencia_detenida` - Competencia detenida
-   `error` - Error en la operación

---

## 🔐 Seguridad

### Tokens JWT

-   **Access Token:** 1 hora de duración
-   **Refresh Token:** 7 días de duración
-   **Almacenamiento:** Seguro (SharedPreferences, AsyncStorage, localStorage)
-   **Transmisión:** Header `Authorization: Bearer {token}` (REST) o Query param (WebSocket)

### Validaciones

1. ✅ Token JWT válido
2. ✅ Juez activo en el sistema
3. ✅ Competencia asignada y activa
4. ✅ Competencia EN CURSO para registrar tiempos
5. ✅ Juez tiene permiso para el equipo
6. ✅ Máximo 15 registros por lote

---

## 🆘 Solución de Problemas

### Error: "Credenciales inválidas"

-   Verifica username y password
-   Asegúrate de que el juez esté activo en el admin

### Error: "Token expirado"

-   Implementa refresh automático del token
-   Ver: [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) - `refreshAccessToken()`

### Error: "La competencia no está en curso"

-   Inicia la competencia desde el panel de admin
-   Ver: [VALIDACION_COMPETENCIA.md](VALIDACION_COMPETENCIA.md)

### Error: "Máximo 15 registros permitidos"

-   Divide los registros en lotes de máximo 15
-   Ver: [REGISTRO_BATCH.md](REGISTRO_BATCH.md)

### WebSocket no conecta

-   Verifica que el servidor Daphne esté corriendo (no runserver)
-   Verifica que el token JWT sea válido
-   Ver: [WEBSOCKET_SIMPLE.md](WEBSOCKET_SIMPLE.md) - "Solución de Problemas"

---

## 📞 Recursos Adicionales

### Herramientas de Desarrollo

-   **Panel Admin:** http://127.0.0.1:8000/admin/
-   **API REST:** http://127.0.0.1:8000/api/
-   **Pruebas WebSocket:** Archivos HTML de prueba

### Tecnologías Utilizadas

-   **Backend:** Django 5.2.8 + Django REST Framework
-   **WebSocket:** Django Channels + Daphne
-   **Autenticación:** SimpleJWT
-   **Base de Datos:** SQLite (desarrollo) / PostgreSQL (producción)

### Comandos Útiles

```bash
# Iniciar servidor WebSocket
uv run daphne -b 127.0.0.1 -p 8000 server.asgi:application

# Crear superusuario
uv run python manage.py createsuperuser

# Migraciones
uv run python manage.py makemigrations
uv run python manage.py migrate

# Recolectar archivos estáticos
uv run python manage.py collectstatic --noinput
```

---

## 📝 Convenciones

### Códigos de Estado HTTP

| Código | Significado           | Uso                                     |
| ------ | --------------------- | --------------------------------------- |
| 200    | OK                    | Operación exitosa                       |
| 205    | Reset Content         | Logout exitoso                          |
| 400    | Bad Request           | Parámetros inválidos                    |
| 401    | Unauthorized          | Credenciales inválidas o token expirado |
| 403    | Forbidden             | Usuario inactivo                        |
| 500    | Internal Server Error | Error del servidor                      |

### Formato de Timestamps

Los tiempos se envían en **milisegundos desde epoch**:

```javascript
// JavaScript
const tiempo = Date.now(); // 1699825200000

// Flutter/Dart
final tiempo = DateTime.now().millisecondsSinceEpoch; // 1699825200000

// Python
import time
tiempo = int(time.time() * 1000) # 1699825200000
```

---

## ✅ Checklist de Integración Completa

Antes de poner en producción, verifica:

### Autenticación

-   [ ] Login funciona correctamente
-   [ ] Tokens se guardan de forma segura
-   [ ] Logout invalida tokens
-   [ ] Refresh token funciona automáticamente

### WebSocket

-   [ ] Conexión WebSocket exitosa
-   [ ] Se manejan todos los tipos de mensajes
-   [ ] Se valida el estado de la competencia
-   [ ] Se implementa reconexión automática

### Registro de Tiempos

-   [ ] Captura de timestamps precisa
-   [ ] Envío de lote de 15 tiempos
-   [ ] Manejo de confirmaciones
-   [ ] Manejo de errores específicos

### UI/UX

-   [ ] Indicador de estado de conexión
-   [ ] Indicador de estado de competencia
-   [ ] Botones habilitados/deshabilitados según estado
-   [ ] Contador de tiempos registrados
-   [ ] Notificaciones de éxito/error

### Robustez

-   [ ] Manejo de errores de red
-   [ ] Reconexión automática
-   [ ] Persistencia de datos no enviados
-   [ ] Logging de eventos importantes

---

## 📖 Orden de Lectura Recomendado

### Para principiantes:

1. **[INICIO_RAPIDO.md](INICIO_RAPIDO.md)** - Conceptos básicos
2. **[WEBSOCKET_SIMPLE.md](WEBSOCKET_SIMPLE.md)** - Tutorial de WebSocket
3. **[EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md)** - Copiar código
4. Probar con `test_registro_batch.html`

### Para desarrolladores experimentados:

1. **[API_DOCUMENTACION.md](API_DOCUMENTACION.md)** - Referencia completa
2. **[FLUJO_COMPLETO.md](FLUJO_COMPLETO.md)** - Arquitectura
3. **[EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md)** - Implementación
4. **[REGISTRO_BATCH.md](REGISTRO_BATCH.md)** - Detalles de batch

---

## 🎓 Siguientes Pasos

1. ✅ Lee [INICIO_RAPIDO.md](INICIO_RAPIDO.md)
2. ✅ Prueba el archivo `test_registro_batch.html`
3. ✅ Copia el código de [EJEMPLOS_CODIGO.md](EJEMPLOS_CODIGO.md) para tu plataforma
4. ✅ Implementa en tu app móvil
5. ✅ Prueba en un entorno controlado
6. ✅ Despliega a producción

---

**Última actualización:** 12 de noviembre de 2025  
**Versión de Documentación:** 1.0
