# 📦 Registro de Tiempos en Lote (Batch)

## Descripción General

El servidor soporta el envío de **múltiples registros de tiempo (hasta 15) en un solo mensaje** a través de WebSocket. Esto está diseñado para que las aplicaciones móviles puedan enviar los 15 tiempos de un equipo de manera eficiente.

---

## 🔄 Flujo de Funcionamiento

### 1️⃣ Conexión WebSocket

```javascript
const ws = new WebSocket(
    `ws://127.0.0.1:8000/ws/juez/${juez_id}/?token=${access_token}`
);
```

### 2️⃣ Enviar Registros en Lote

```javascript
const mensaje = {
    tipo: "registrar_tiempos", // Nuevo tipo de mensaje
    equipo_id: 1,
    registros: [
        {
            tiempo: 123456,
            horas: 0,
            minutos: 2,
            segundos: 3,
            milisegundos: 456,
        },
        {
            tiempo: 234567,
            horas: 0,
            minutos: 3,
            segundos: 54,
            milisegundos: 567,
        },
        // ... hasta 15 registros
    ],
};

ws.send(JSON.stringify(mensaje));
```

### 3️⃣ Respuesta del Servidor

```json
{
    "tipo": "tiempos_registrados_batch",
    "equipo_id": 1,
    "total_enviados": 15,
    "total_guardados": 14,
    "total_fallidos": 1,
    "registros_guardados": [
        {
            "indice": 0,
            "id_registro": "abc123def456...",
            "tiempo": 123456
        }
        // ...
    ],
    "registros_fallidos": [
        {
            "indice": 7,
            "error": "El tiempo no puede ser negativo"
        }
    ]
}
```

---

## 📋 Especificación del Mensaje

### Campos Requeridos

| Campo       | Tipo    | Descripción                            |
| ----------- | ------- | -------------------------------------- |
| `tipo`      | string  | Debe ser `"registrar_tiempos"`         |
| `equipo_id` | integer | ID del equipo                          |
| `registros` | array   | Array de objetos de tiempo (máximo 15) |

### Estructura de Cada Registro

| Campo          | Tipo    | Requerido | Descripción                  |
| -------------- | ------- | --------- | ---------------------------- |
| `tiempo`       | integer | Sí        | Tiempo total en milisegundos |
| `horas`        | integer | No        | Componente de horas          |
| `minutos`      | integer | No        | Componente de minutos        |
| `segundos`     | integer | No        | Componente de segundos       |
| `milisegundos` | integer | No        | Componente de milisegundos   |

---

## ✅ Validaciones

### A Nivel de Mensaje

1. **Autenticación**: El juez debe estar autenticado con JWT válido
2. **Competencia Activa**: `competencia.en_curso` debe ser `True`
3. **Equipo ID**: Debe ser un entero válido
4. **Array de Registros**: Debe existir y ser un array
5. **Límite**: Máximo 15 registros por lote

### A Nivel de Registro Individual

1. **Tiempo**: Debe ser un entero
2. **Permiso**: El juez debe tener asignado ese equipo
3. **Duplicados**: No se permiten tiempos duplicados

---

## 🎯 Códigos de Respuesta

### Exitosa (Todos guardados)

```json
{
    "tipo": "tiempos_registrados_batch",
    "equipo_id": 1,
    "total_enviados": 15,
    "total_guardados": 15,
    "total_fallidos": 0,
    "registros_guardados": [...],
    "registros_fallidos": []
}
```

### Parcial (Algunos fallidos)

```json
{
    "tipo": "tiempos_registrados_batch",
    "equipo_id": 1,
    "total_enviados": 15,
    "total_guardados": 13,
    "total_fallidos": 2,
    "registros_guardados": [...],
    "registros_fallidos": [
        {
            "indice": 5,
            "error": "Ya existe un registro con este tiempo"
        },
        {
            "indice": 9,
            "error": "El tiempo no puede ser negativo"
        }
    ]
}
```

### Error Completo

```json
{
    "tipo": "error",
    "mensaje": "Debes enviar un array de registros",
    "codigo": "array_requerido"
}
```

---

## 🛡️ Manejo de Errores

### Errores de Validación de Lote

| Error            | Mensaje                                         |
| ---------------- | ----------------------------------------------- |
| No hay equipo_id | "equipo_id es requerido"                        |
| No hay registros | "Debes enviar un array de registros"            |
| No es array      | "Los registros deben ser un array"              |
| Más de 15        | "No puedes enviar más de 15 registros a la vez" |

### Errores por Registro Individual

-   El registro se marca como fallido pero **no detiene** el procesamiento
-   El servidor continúa procesando los demás registros
-   Los errores se reportan en el array `registros_fallidos`

---

## 📱 Ejemplo de Implementación (JavaScript)

```javascript
class RegistroTiemposBatch {
    constructor(juezId, token) {
        this.juezId = juezId;
        this.token = token;
        this.ws = null;
    }

    conectar() {
        return new Promise((resolve, reject) => {
            this.ws = new WebSocket(
                `ws://127.0.0.1:8000/ws/juez/${this.juezId}/?token=${this.token}`
            );

            this.ws.onopen = () => resolve();
            this.ws.onerror = () => reject("Error de conexión");

            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.manejarMensaje(data);
            };
        });
    }

    enviarTiempos(equipoId, tiempos) {
        if (this.ws.readyState !== WebSocket.OPEN) {
            throw new Error("WebSocket no conectado");
        }

        if (tiempos.length > 15) {
            throw new Error("Máximo 15 registros por lote");
        }

        const mensaje = {
            tipo: "registrar_tiempos",
            equipo_id: equipoId,
            registros: tiempos,
        };

        this.ws.send(JSON.stringify(mensaje));
    }

    manejarMensaje(data) {
        switch (data.tipo) {
            case "tiempos_registrados_batch":
                console.log(`✅ Guardados: ${data.total_guardados}`);
                console.log(`❌ Fallidos: ${data.total_fallidos}`);

                if (data.total_fallidos > 0) {
                    console.warn("Errores:", data.registros_fallidos);
                }
                break;

            case "error":
                console.error("Error del servidor:", data.mensaje);
                break;
        }
    }
}

// Uso:
async function registrarEquipo() {
    const registro = new RegistroTiemposBatch(1, "mi_token_jwt");
    await registro.conectar();

    const tiempos = [
        { tiempo: 900000, horas: 0, minutos: 15, segundos: 0, milisegundos: 0 },
        {
            tiempo: 950000,
            horas: 0,
            minutos: 15,
            segundos: 50,
            milisegundos: 0,
        },
        // ... hasta 15 tiempos
    ];

    registro.enviarTiempos(1, tiempos);
}
```

---

## 🔍 Diferencias con Registro Individual

### Registro Individual (anterior)

```json
{
    "tipo": "registrar_tiempo",
    "equipo_id": 1,
    "tiempo": 123456
}
```

**Respuesta:**

```json
{
    "tipo": "tiempo_registrado",
    "equipo_id": 1,
    "tiempo": 123456,
    "id_registro": "abc123..."
}
```

### Registro en Lote (nuevo)

```json
{
    "tipo": "registrar_tiempos",
    "equipo_id": 1,
    "registros": [{ "tiempo": 123456 }, { "tiempo": 234567 }]
}
```

**Respuesta:**

```json
{
    "tipo": "tiempos_registrados_batch",
    "equipo_id": 1,
    "total_enviados": 2,
    "total_guardados": 2,
    "total_fallidos": 0,
    "registros_guardados": [...],
    "registros_fallidos": []
}
```

---

## 🚀 Ventajas del Registro en Lote

1. ✅ **Eficiencia**: Una sola conexión WebSocket para 15 tiempos
2. ✅ **Menor latencia**: No hay delay entre envíos
3. ✅ **Transaccional**: Se procesan todos los registros válidos
4. ✅ **Retroalimentación**: Sabes exactamente cuáles fallaron
5. ✅ **Retrocompatibilidad**: El endpoint individual sigue funcionando

---

## 📊 Pruebas

### Archivo de Prueba HTML

Abre `test_registro_batch.html` en tu navegador:

1. Inicia sesión con tus credenciales
2. El WebSocket se conectará automáticamente
3. Ingresa el ID del equipo
4. Haz clic en "Enviar 15 Registros"
5. Observa el resultado en tiempo real

### Comando cURL (no soportado)

⚠️ **Nota**: El registro de tiempos **solo funciona vía WebSocket**, no con HTTP/REST.

---

## ❓ Preguntas Frecuentes

### ¿Puedo enviar menos de 15 registros?

✅ **Sí**, puedes enviar desde 1 hasta 15 registros.

### ¿Qué pasa si envío más de 15?

❌ El servidor rechazará el mensaje completo con error.

### ¿Se detiene el procesamiento si uno falla?

❌ **No**, el servidor continúa procesando todos los registros válidos.

### ¿Puedo mezclar registros de diferentes equipos?

❌ **No**, todos los registros en un lote deben ser del mismo equipo.

### ¿El registro individual sigue funcionando?

✅ **Sí**, el endpoint `registrar_tiempo` sigue disponible para compatibilidad.

---

## 🔧 Solución de Problemas

### Error: "No puedes enviar más de 15 registros"

**Solución**: Divide tu array en lotes de máximo 15 registros.

### Error: "La competencia no está en curso"

**Solución**: Asegúrate de que la competencia esté activa en el admin panel.

### Error: "No tienes permiso para registrar tiempos de este equipo"

**Solución**: Verifica que el juez tenga asignado ese equipo.

### Algunos registros fallan

**Solución**: Revisa el array `registros_fallidos` en la respuesta para ver los errores específicos.

---

## 📝 Notas Importantes

1. El procesamiento es **secuencial**, no paralelo
2. Los índices en `registros_fallidos` corresponden al array original (base 0)
3. El `id_registro` es un UUID único por cada tiempo guardado
4. Los registros se guardan **en el orden del array**

---

## 🎓 Resumen

-   **Tipo de mensaje**: `registrar_tiempos`
-   **Máximo por lote**: 15 registros
-   **Respuesta**: `tiempos_registrados_batch`
-   **Manejo de errores**: Continúa procesando registros válidos
-   **Retrocompatibilidad**: Registro individual sigue funcionando
