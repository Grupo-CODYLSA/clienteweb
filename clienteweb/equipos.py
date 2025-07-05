# Contenido para: app/equipos.py

import requests
import json

# IMPORTANTE: Es una mala práctica tener credenciales en el código.
# Lo ideal es guardarlas en variables de entorno o en el settings.py de Django.
# Por ahora, las ponemos aquí para que el ejemplo sea claro.
SAP_HOST = "https://181.119.121.70:50000/b1s/v1"
SAP_COMPANY_DB = "CISMA" # Reemplaza con tu base de datos
SAP_USER = "manager" # Reemplaza con tu usuario
SAP_PASSWORD = "Initial0!" # Reemplaza con tu contraseña

def get_sap_session():
    """
    Inicia sesión en SAP Service Layer y devuelve la sesión con la cookie.
    Devuelve None si falla.
    """
    login_data = {
        "CompanyDB": SAP_COMPANY_DB,
        "UserName": SAP_USER,
        "Password": SAP_PASSWORD
    }
    
    try:
        # 'verify=False' es para ignorar errores de certificado SSL. En producción, deberías usar un certificado válido.
        response = requests.post(f"{SAP_HOST}/Login", json=login_data, verify=False, timeout=10)
        response.raise_for_status()  # Lanza un error si la respuesta no es 2xx
        
        # Creamos una sesión de requests que reutilizará la cookie
        sap_session = requests.Session()
        sap_session.cookies.update(response.cookies)
        sap_session.verify = False # Aplicamos la misma configuración de SSL a la sesión
        
        print(">>> Conexión exitosa a SAP Service Layer.")
        return sap_session

    except requests.exceptions.RequestException as e:
        print(f"!!! Error al conectar con SAP Service Layer: {e}")
        return None

def get_equipo_details(equipment_code):
    """
    Obtiene los detalles completos de un equipo específico desde SAP.
    """
    sap_session = get_sap_session()
    
    if not sap_session:
        return None # No se pudo iniciar sesión

    # El endpoint para un equipo específico, usando el código proporcionado
    # El formato es 'NombreDeLaVista'('Codigo')
    url = f"{SAP_HOST}/VID_MTEQUIPOS('{equipment_code}')"
    
    print(f">>> Consultando SAP para el equipo: {equipment_code}")
    print(f">>> URL: {url}")
    
    try:
        response = sap_session.get(url, timeout=10)
        response.raise_for_status()
        
        equipo_data = response.json()
        print(">>> Datos recibidos de SAP:", json.dumps(equipo_data, indent=2))
        return equipo_data

    except requests.exceptions.RequestException as e:
        print(f"!!! Error al obtener detalles del equipo '{equipment_code}': {e}")
        return None
    finally:
        # Cerramos la sesión de SAP
        if sap_session:
            sap_session.post(f"{SAP_HOST}/Logout")
            print(">>> Sesión de SAP cerrada.")