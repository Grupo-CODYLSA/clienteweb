# app/sap_service.py

import requests
import json

# --- Configuración de SAP ---
SAP_HOST = "https://181.119.121.70:50000"
SAP_COMPANY = "CIMSA"
SAP_USER = "manager"
SAP_PASSWORD = "Initial0!"

def get_sap_data(endpoint_url):
    """
    Se conecta a SAP Service Layer y obtiene TODOS los datos de un endpoint,
    manejando la paginación de SAP automáticamente.
    """
    session = requests.Session()
    session.verify = False
    requests.packages.urllib3.disable_warnings()

    all_data = []

    try:
        # 1. Iniciar sesión en SAP
        login_data = {
            "CompanyDB": SAP_COMPANY,
            "UserName": SAP_USER,
            "Password": SAP_PASSWORD
        }
        login_url = f"{SAP_HOST}/b1s/v1/Login"
        login_response = session.post(login_url, json=login_data, timeout=15)
        login_response.raise_for_status()

        # 2. Bucle para obtener todas las páginas
        next_link = endpoint_url
        
        while next_link:
            print(f"Obteniendo datos de: {next_link}")
            data_response = session.get(next_link, timeout=30)
            data_response.raise_for_status()
            
            data = data_response.json()
            
            if 'value' in data:
                all_data.extend(data['value'])
            
            # =================================================================
            #                       LA CORRECCIÓN ESTÁ AQUÍ
            # =================================================================
            # Buscamos la clave "odata.nextLink" SIN el símbolo "@"
            next_link = data.get('odata.nextLink') 
            
            if next_link:
                print(f"Encontrado nextLink. Pidiendo siguiente página...")
                # Si el enlace es relativo, lo hacemos absoluto
                if not next_link.startswith('http'):
                    next_link = f"{SAP_HOST}/b1s/v1/{next_link}"

        print(f"¡Éxito! Se obtuvieron un total de {len(all_data)} registros.")
        return all_data

    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con SAP: {e}")
        return []