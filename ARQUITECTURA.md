# 🏗️ Arquitectura del Sistema de Carrera 5K

## 📋 Resumen

Este documento describe la arquitectura final del sistema de gestión de carreras 5K, con énfasis en la separación de roles entre **Admin (Django User)** y **Juez (Modelo personalizado)**.

---

## 🎯 Concepto Clave

### Dos Sistemas de Autenticación Separados

1. **Admin de Django**: Usuario estándar de Django para el panel de administración
2. **Juez**: Modelo personalizado con autenticación JWT para API y WebSocket

---

## 👥 Roles y Accesos

### 1. **Admin (Django User)**

-   **Propósito**: Gestión del sistema a través del panel de administración
-   **Autenticación**: Sistema estándar de Django (username/password)
-   **Accesos**:
    -   ✅ Panel de administración de Django (`/admin/`)
    -   ✅ CRUD completo de Competencias, Jueces, Equipos
    -   ✅ Visualización de registros de tiempos
    -   ❌ NO tiene acceso a la API REST
    -   ❌ NO puede conectarse vía WebSocket

### 2. **Juez (Modelo Personalizado)**

-   **Propósito**: Registrar tiempos durante las carreras
-   **Autenticación**: JWT tokens (access + refresh)
-   **Accesos**:
    -   ✅ Login vía API (`/api/login/`)
    -   ✅ Conexión WebSocket para registrar tiempos
    -   ✅ Endpoints de la API REST
    -   ❌ NO tiene acceso al panel de administración
    -   ❌ NO es un usuario de Django

---

## 🔐 Sistema de Autenticación

### Para Admin (Django User)

```python
# Crear superusuario
python manage.py createsuperuser

# Login
http://127.0.0.1:8000/admin/
Username: admin
Password: admin
```

### Para Juez (JWT)

```python
# 1. Login - POST /api/login/
{
    "username": "juez1",
    "password": "password123"
}

# Respuesta:
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "juez": {
        "id": 1,
        "username": "juez1",
        "competencia_id": 1,
        "activo": true
    }
}

# 2. Usar access token en headers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...

# 3. Refrescar token - POST /api/token/refresh/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

# 4. Logout - POST /api/logout/
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 🗄️ Modelos de Datos

### Competencia

```python
- nombre: CharField(200)
- fecha_hora: DateTimeField
- categoria: CharField(choices: estudiantes, interfacultades)
- activa: BooleanField
- en_curso: BooleanField
- fecha_inicio: DateTimeField (nullable)
- fecha_fin: DateTimeField (nullable)
```

### Juez (NO hereda de AbstractUser)

```python
- username: CharField(150, unique=True)
- password: CharField(128)  # Hasheado con make_password()
- competencia: ForeignKey(Competencia)
- activo: BooleanField

# Métodos personalizados:
- set_password(raw_password)  # Hashea la contraseña
- check_password(raw_password)  # Verifica la contraseña
```

### Equipo

```python
- nombre: CharField(200)
- dorsal: IntegerField
- juez_asignado: ForeignKey(Juez)

# Property calculada:
- competencia (retorna juez_asignado.competencia)
```

### RegistroTiempo

```python
- id_registro: UUIDField (unique, auto)
- equipo: ForeignKey(Equipo)
- tiempo: BigIntegerField (milisegundos)
- horas: IntegerField
- minutos: IntegerField
- segundos: IntegerField
- milisegundos: IntegerField
- timestamp: DateTimeField (auto_now_add)
```

---

## 🔌 Endpoints de la API

### Autenticación

| Método | Endpoint              | Descripción                                     | Auth |
| ------ | --------------------- | ----------------------------------------------- | ---- |
| POST   | `/api/login/`         | Login de juez (retorna access + refresh tokens) | ❌   |
| POST   | `/api/logout/`        | Logout (blacklist del refresh token)            | ✅   |
| POST   | `/api/token/refresh/` | Refrescar access token                          | ❌   |

### Registros

| Método | Endpoint          | Descripción                   | Auth |
| ------ | ----------------- | ----------------------------- | ---- |
| POST   | `/api/registrar/` | Registrar tiempo de un equipo | ✅   |

---

## 🌐 WebSocket

### Conexión

```javascript
// URL del WebSocket
ws://127.0.0.1:8000/ws/juez/

// Autenticación en query params
ws://127.0.0.1:8000/ws/juez/?token=<access_token>

// El servidor valida el token y obtiene el juez
// Solo acepta equipos asignados a ese juez
```

### Mensajes

#### Registrar Tiempo

```json
{
    "tipo": "registrar_tiempo",
    "equipo_id": 1,
    "tiempo": 1234567,
    "horas": 0,
    "minutos": 20,
    "segundos": 34,
    "milisegundos": 567
}
```

#### Respuesta Exitosa

```json
{
    "tipo": "tiempo_registrado",
    "registro": {
        "id_registro": "123e4567-e89b-12d3-a456-426614174000",
        "equipo_id": 1,
        "equipo_nombre": "Equipo Rojo",
        "tiempo": 1234567,
        "timestamp": "2025-11-11T23:00:00Z"
    }
}
```

#### Error

```json
{
    "tipo": "error",
    "mensaje": "El equipo con ID 1 no pertenece a tu lista de equipos asignados"
}
```

---

## 🛠️ Configuración Técnica

### Settings.py

```python
# NO hay AUTH_USER_MODEL personalizado
# Se usa el User de Django por defecto para admin

# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'BLACKLIST_AFTER_ROTATION': True,
}

# REST Framework usa custom authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'app.authentication.JuezJWTAuthentication',
    ),
}
```

### Autenticación Personalizada

```python
# app/authentication.py
class JuezJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        juez_id = validated_token.get('juez_id')
        juez = Juez.objects.get(id=juez_id, activo=True)
        return juez
```

### Admin de Juez

```python
# app/admin.py
class JuezForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def save(self, commit=True):
        juez = super().save(commit=False)
        juez.set_password(self.cleaned_data["password1"])
        if commit:
            juez.save()
        return juez

@admin.register(Juez)
class JuezAdmin(admin.ModelAdmin):
    form = JuezForm
    list_display = ['username', 'competencia', 'activo']
    list_filter = ['competencia', 'activo']
```

---

## 📊 Flujo de Trabajo

### 1. Configuración Inicial (Admin)

1. Admin ingresa al panel Django (`/admin/`)
2. Crea una **Competencia**
3. Crea **Jueces** asignándolos a la competencia
4. Crea **Equipos** asignándolos a cada juez

### 2. Durante la Carrera (Juez)

1. Juez hace login vía API (`/api/login/`)
2. Recibe `access_token` y `refresh_token`
3. Se conecta al WebSocket con el `access_token`
4. Registra tiempos enviando mensajes JSON
5. El servidor valida que el equipo pertenezca al juez
6. Registros se guardan en la base de datos

### 3. Post-Carrera (Admin)

1. Admin accede al panel Django
2. Visualiza todos los registros de tiempo
3. Puede exportar/analizar datos
4. Desactiva la competencia

---

## 🔒 Seguridad

### Separación de Roles

-   ✅ Admin y Juez son **completamente independientes**
-   ✅ Juez **NO puede** acceder al panel de administración
-   ✅ Admin **NO puede** usar la API de jueces
-   ✅ Cada juez solo puede registrar tiempos de **sus equipos asignados**

### Tokens JWT

-   ✅ Access token expira en 1 hora
-   ✅ Refresh token expira en 7 días
-   ✅ Logout implementa blacklist de tokens
-   ✅ WebSocket valida token en cada conexión

### Contraseñas

-   ✅ Passwords de jueces hasheados con `make_password()`
-   ✅ Validación con `check_password()`
-   ✅ No se almacenan en texto plano

---

## 🧪 Datos de Prueba

### Credenciales

```bash
# Admin Django
Username: admin
Password: admin
URL: http://127.0.0.1:8000/admin/

# Juez 1
Username: juez1
Password: password123
Equipos: Rojo (#1), Azul (#2), Verde (#3)

# Juez 2
Username: juez2
Password: password123
Equipos: Amarillo (#4), Naranja (#5)
```

### Recrear Datos

```bash
# Eliminar BD y recrear
Remove-Item db.sqlite3
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Crear datos de prueba
python create_test_data.py
```

---

## 📝 Comandos Útiles

```bash
# Activar entorno virtual
.\.venv\Scripts\Activate.ps1

# Iniciar servidor
python manage.py runserver

# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear datos de prueba
python create_test_data.py

# Acceder a shell de Django
python manage.py shell
```

---

## 📚 Archivos Importantes

```
Server5K/
├── app/
│   ├── models.py          # Modelos: Competencia, Juez, Equipo, RegistroTiempo
│   ├── views.py           # LoginView, LogoutView, RegistrarTiempoView
│   ├── authentication.py  # JuezJWTAuthentication (custom)
│   ├── consumers.py       # JuezConsumer (WebSocket)
│   ├── admin.py           # Admin de Django con JuezForm
│   └── urls.py            # Rutas de la API
├── server/
│   └── settings.py        # Configuración JWT y REST Framework
├── db.sqlite3             # Base de datos SQLite
├── create_test_data.py    # Script para datos de prueba
└── ARQUITECTURA.md        # Este documento
```

---

## ✅ Checklist de Implementación

-   [x] Modelo Juez como modelo standalone (NO AbstractUser)
-   [x] Custom authentication backend (JuezJWTAuthentication)
-   [x] LoginView retorna access + refresh tokens
-   [x] LogoutView implementa blacklist
-   [x] WebSocket valida JWT y obtiene juez
-   [x] JuezAdmin con formulario personalizado para passwords
-   [x] Separación completa entre Admin y Juez
-   [x] Migraciones limpias y aplicadas
-   [x] Datos de prueba funcionales
-   [x] Servidor corriendo sin errores

---

## 🎉 Conclusión

El sistema ahora tiene una **arquitectura limpia y segura** con:

1. **Admin de Django**: Para gestión administrativa del sistema
2. **Juez con JWT**: Para registro de tiempos en tiempo real vía API/WebSocket
3. **Separación total**: Cada rol tiene sus propios permisos y accesos
4. **Seguridad**: Tokens JWT, passwords hasheados, validación de permisos

Esta arquitectura es **escalable, mantenible y segura** para producción. 🚀
