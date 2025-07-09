# clienteweb/logica_statusdoc.py

import requests
import json

# --- Configuración de la Conexión a SAP B1 Service Layer ---
# Lo ideal es guardar esto en el settings.py de Django o en variables de entorno.
SAP_BASE_URL = "https://181.119.121.70:50000/b1s/v1"
SAP_COMPANY_DB = "CIMSA"  # Reemplaza con el nombre de tu base de datos de SAP
SAP_USER = "manager"         # Reemplaza con tu usuario
SAP_PASSWORD = "Initial0!"   # Reemplaza con tu contraseña


def fetch_sap_status_docs(estado=None):
    """
    Se conecta a SAP y obtiene TODOS los documentos, manejando la paginación
    automáticamente siguiendo los '@odata.nextLink'.
    """
    session = requests.Session()
    session.verify = False

    login_payload = {
        "CompanyDB": SAP_COMPANY_DB,
        "UserName": SAP_USER,
        "Password": SAP_PASSWORD
    }
    
    try:
        login_url = f"{SAP_BASE_URL}/Login"
        login_response = session.post(login_url, data=json.dumps(login_payload), timeout=15)
        login_response.raise_for_status()
        print("✅ Conexión a SAP exitosa.")
    except requests.exceptions.RequestException as e:
        print(f"❌ Error al conectar a SAP B1: {e}")
        return []

    # --- LÓGICA DE PAGINACIÓN ---
    todos_los_documentos = []
    
    # 1. Construimos la URL inicial
    url_a_consultar = f"{SAP_BASE_URL}/sml.svc/STATUSDOC"
    if estado:
        url_a_consultar += f"?$filter=EstadodeDocumento eq '{estado}'"

    try:
        # 2. Iniciamos un bucle que continuará mientras haya una URL por consultar
        while url_a_consultar:
            print(f"🚀 Consultando página: {url_a_consultar}")
            
            docs_response = session.get(url_a_consultar, timeout=15)
            docs_response.raise_for_status()
            response_data = docs_response.json()
            
            # 3. Añadimos los resultados de la página actual a nuestra lista principal
            if 'value' in response_data:
                todos_los_documentos.extend(response_data['value'])
            
            # 4. Verificamos si hay una página siguiente
            if '@odata.nextLink' in response_data:
                # Construimos la URL completa para la siguiente página
                siguiente_enlace = response_data['@odata.nextLink']
                url_a_consultar = f"{SAP_BASE_URL}/sml.svc/{siguiente_enlace}"
            else:
                # Si no hay 'nextLink', terminamos el bucle
                url_a_consultar = None
        
        return todos_los_documentos

    except requests.exceptions.RequestException as e:
        print(f"❌ Error durante la obtención de documentos paginados: {e}")
        return [] # Devolvemos lo que hayamos juntado hasta ahora, o una lista vacía
    finally:
        session.post(f"{SAP_BASE_URL}/Logout")
        print("🔌 Sesión de SAP cerrada.")
