"""
Script para crear datos de prueba
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
django.setup()

from app.models import Competencia, Juez, Equipo

# Crear competencia de prueba
from datetime import datetime
from django.utils import timezone

competencia, created = Competencia.objects.get_or_create(
    nombre="Carrera 5K Noviembre 2025",
    defaults={
        'fecha_hora': timezone.make_aware(datetime(2025, 11, 15, 8, 0, 0)),
        'categoria': "estudiantes",
        'activa': True,
        'en_curso': False
    }
)
if created:
    print(f"✅ Competencia creada: {competencia.nombre}")
else:
    print(f"ℹ️  Competencia ya existe: {competencia.nombre}")

# Crear jueces de prueba
juez1, created = Juez.objects.get_or_create(
    username="juez1",
    defaults={
        'competencia': competencia,
        'activo': True
    }
)
if created:
    juez1.set_password("password123")
    juez1.save()
    print(f"✅ Juez creado: {juez1.username} - Contraseña: password123")
else:
    print(f"ℹ️  Juez ya existe: {juez1.username}")

juez2, created = Juez.objects.get_or_create(
    username="juez2",
    defaults={
        'competencia': competencia,
        'activo': True
    }
)
if created:
    juez2.set_password("password123")
    juez2.save()
    print(f"✅ Juez creado: {juez2.username} - Contraseña: password123")
else:
    print(f"ℹ️  Juez ya existe: {juez2.username}")

# Crear equipos de prueba
equipos_juez1 = [
    ("Equipo Rojo", 1),
    ("Equipo Azul", 2),
    ("Equipo Verde", 3),
]

equipos_juez2 = [
    ("Equipo Amarillo", 4),
    ("Equipo Naranja", 5),
]

print("\n🏃 Creando equipos para Juez 1:")
for nombre, dorsal in equipos_juez1:
    equipo, created = Equipo.objects.get_or_create(
        juez_asignado=juez1,
        dorsal=dorsal,
        defaults={'nombre': nombre}
    )
    if created:
        print(f"✅ Equipo creado: {equipo.nombre} - Dorsal #{equipo.dorsal}")
    else:
        print(f"ℹ️  Equipo ya existe: {equipo.nombre} - Dorsal #{equipo.dorsal}")

print("\n🏃 Creando equipos para Juez 2:")
for nombre, dorsal in equipos_juez2:
    equipo, created = Equipo.objects.get_or_create(
        juez_asignado=juez2,
        dorsal=dorsal,
        defaults={'nombre': nombre}
    )
    if created:
        print(f"✅ Equipo creado: {equipo.nombre} - Dorsal #{equipo.dorsal}")
    else:
        print(f"ℹ️  Equipo ya existe: {equipo.nombre} - Dorsal #{equipo.dorsal}")

print("\n" + "="*50)
print("🎉 Datos de prueba creados exitosamente!")
print("="*50)
print("\nCredenciales de prueba:")
print("  👤 Admin Django: admin / admin")
print("  🏃 Juez 1: juez1 / password123")
print("  🏃 Juez 2: juez2 / password123")
print("\nPuedes acceder al admin en: http://127.0.0.1:8000/admin/")
print("="*50)
