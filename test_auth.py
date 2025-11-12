"""
Script de ejemplo para probar el sistema de autenticación JWT de jueces
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def print_response(title, response):
    """Imprime la respuesta de manera bonita"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    print(f"{'='*60}\n")

def test_login():
    """Test: Login de juez"""
    print("\n🔐 TEST 1: LOGIN DE JUEZ")
    
    url = f"{BASE_URL}/login/"
    data = {
        "username": "juez1",
        "password": "password123"
    }
    
    response = requests.post(url, json=data)
    print_response("Login Response", response)
    
    if response.status_code == 200:
        tokens = response.json()
        return tokens['access'], tokens['refresh']
    return None, None

def test_refresh_token(refresh_token):
    """Test: Refrescar access token"""
    print("\n🔄 TEST 2: REFRESCAR TOKEN")
    
    url = f"{BASE_URL}/token/refresh/"
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(url, json=data)
    print_response("Refresh Token Response", response)
    
    if response.status_code == 200:
        return response.json()['access']
    return None

def test_protected_endpoint(access_token):
    """Test: Acceder a endpoint protegido"""
    print("\n🔒 TEST 3: ACCEDER A ENDPOINT PROTEGIDO")
    
    url = f"{BASE_URL}/enviar_tiempos/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "equipo_id": 1,
        "registros": [
            {
                "tiempo": 1234567,
                "timestamp": "2025-11-11T23:00:00Z"
            }
        ]
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response("Protected Endpoint Response", response)

def test_logout(access_token, refresh_token):
    """Test: Logout (blacklist de refresh token)"""
    print("\n🚪 TEST 4: LOGOUT")
    
    url = f"{BASE_URL}/logout/"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    data = {
        "refresh": refresh_token
    }
    
    response = requests.post(url, json=data, headers=headers)
    print_response("Logout Response", response)

def test_invalid_credentials():
    """Test: Login con credenciales inválidas"""
    print("\n❌ TEST 5: LOGIN CON CREDENCIALES INVÁLIDAS")
    
    url = f"{BASE_URL}/login/"
    data = {
        "username": "juez1",
        "password": "wrongpassword"
    }
    
    response = requests.post(url, json=data)
    print_response("Invalid Login Response", response)

def test_missing_credentials():
    """Test: Login sin credenciales"""
    print("\n❌ TEST 6: LOGIN SIN CREDENCIALES")
    
    url = f"{BASE_URL}/login/"
    data = {
        "username": "juez1"
    }
    
    response = requests.post(url, json=data)
    print_response("Missing Credentials Response", response)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🧪 TESTING SISTEMA DE AUTENTICACIÓN JWT PARA JUECES")
    print("="*60)
    
    try:
        # Test 1: Login exitoso
        access_token, refresh_token = test_login()
        
        if access_token and refresh_token:
            # Test 2: Refrescar token
            new_access_token = test_refresh_token(refresh_token)
            
            # Test 3: Acceder a endpoint protegido
            if new_access_token:
                test_protected_endpoint(new_access_token)
            
            # Test 4: Logout
            test_logout(access_token, refresh_token)
        
        # Test 5: Login con credenciales inválidas
        test_invalid_credentials()
        
        # Test 6: Login sin credenciales
        test_missing_credentials()
        
        print("\n" + "="*60)
        print("✅ TODOS LOS TESTS COMPLETADOS")
        print("="*60 + "\n")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: No se pudo conectar al servidor.")
        print("Asegúrate de que el servidor esté corriendo en http://127.0.0.1:8000")
        print("Ejecuta: python manage.py runserver\n")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {str(e)}\n")
