# Script para crear datos de prueba
# Ejecutar con: python manage.py shell < crear_datos_prueba.py

from django.utils import timezone
from app.models import Competencia, Juez, Equipo

# Crear competencia
print("Creando competencia...")
competencia = Competencia.objects.create(
    nombre='Carrera 5K Universidad 2025',
    fecha_hora=timezone.now(),
    categoria='estudiantes',
    activa=True
)
print(f"✅ Competencia creada: {competencia}")

# Crear jueces (ahora son usuarios completos)
print("\nCreando jueces...")

juez1 = Juez.objects.create_user(
    username='juez1',
    password='password123',
    first_name='Juan',
    last_name='Pérez',
    email='juez1@example.com',
    competencia=competencia,
    activo=True,
    telefono='0991234567'
)
print(f"✅ Juez creado: {juez1.username} - {juez1.get_full_name()}")

juez2 = Juez.objects.create_user(
    username='juez2',
    password='password123',
    first_name='María',
    last_name='González',
    email='juez2@example.com',
    competencia=competencia,
    activo=True,
    telefono='0997654321'
)
print(f"✅ Juez creado: {juez2.username} - {juez2.get_full_name()}")

# Crear equipos
print("\nCreando equipos...")

equipos_juez1 = [
    {'nombre': 'Equipo Azul', 'dorsal': 1},
    {'nombre': 'Equipo Rojo', 'dorsal': 2},
    {'nombre': 'Equipo Verde', 'dorsal': 3},
]

equipos_juez2 = [
    {'nombre': 'Equipo Amarillo', 'dorsal': 4},
    {'nombre': 'Equipo Naranja', 'dorsal': 5},
    {'nombre': 'Equipo Morado', 'dorsal': 6},
]

for eq_data in equipos_juez1:
    equipo = Equipo.objects.create(
        nombre=eq_data['nombre'],
        dorsal=eq_data['dorsal'],
        juez_asignado=juez1
    )
    print(f"✅ Equipo creado: {equipo.nombre} (Dorsal {equipo.dorsal}) - Juez: {juez1.username}")

for eq_data in equipos_juez2:
    equipo = Equipo.objects.create(
        nombre=eq_data['nombre'],
        dorsal=eq_data['dorsal'],
        juez_asignado=juez2
    )
    print(f"✅ Equipo creado: {equipo.nombre} (Dorsal {equipo.dorsal}) - Juez: {juez2.username}")

print("\n" + "="*60)
print("✅ DATOS DE PRUEBA CREADOS EXITOSAMENTE")
print("="*60)
print("\n📋 CREDENCIALES:")
print("-" * 60)
print("Juez 1:")
print(f"  Usuario: juez1")
print(f"  Password: password123")
print(f"  ID: {juez1.id}")
print()
print("Juez 2:")
print(f"  Usuario: juez2")
print(f"  Password: password123")
print(f"  ID: {juez2.id}")
print("-" * 60)
print("\n💡 NOTA:")
print("  El superusuario 'admin' debe crearse con:")
print("  python manage.py createsuperuser")
print("-" * 60)
print("\n🔗 URLs de prueba:")
print(f"  Admin: http://localhost:8000/admin/")
print(f"  Login API: http://localhost:8000/api/login/")
print(f"  WebSocket Juez1: ws://localhost:8000/ws/juez/{juez1.id}/?token=<TOKEN>")
print(f"  WebSocket Juez2: ws://localhost:8000/ws/juez/{juez2.id}/?token=<TOKEN>")
print("="*60)
