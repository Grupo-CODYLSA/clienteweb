import requests
import logging
# clase que se encarga de la conexion a la api de SAP B1, Service Layer
class Api_SL():
    def __init__(self,url) -> None:
        self.__url = url
        self.__endpoint_login = "/Login"
        self.__endpoint_logout = "/Logout"
        self._session_id = None
        
    # conexion a la api de SAP B1, Service Layer
    def connect_api(self, empresa, config_data) -> None:
        # obtengo la url con el endpoint de login, header sin utilizar
        url_login,header  = self.set_endpoint(self.__endpoint_login)
        # defino los headers necesarios para la requests
        login_headers = {'Content-Type': 'application/json'}
        # body con las credenciales para el acceso a la api de la empresa en cuestion
        login_body = {
            "CompanyDB": config_data["login_credentials"]['CompanyDB'][empresa],
            "UserName": config_data["login_credentials"]["UserName"],
            "Password": config_data["login_credentials"]["Password"]
        }
        
        try:
            # Realizar la solicitud de login
            login_response = requests.post(
                url_login,
                json=login_body,
                headers=login_headers,
                verify=False,
                timeout=30)
            login_response.raise_for_status()  # Verificar si hay errores en la respuesta
            # Extraer el SessionId de la respuesta, y la almaceno en la variable privada de la clase
            self._session_id = login_response.json().get('SessionId')
            logging.info("Login exitoso API.")
        except requests.exceptions.HTTPError as e:
            logging.error("Error al conectar a la API: %s", e)
            self._session_id = None
        
    def disconnect_api(self):
        url_logout,headers  = self.set_endpoint(self.__endpoint_logout)
        # post al endpoint /Logout
        try:
            response = requests.post(
                url_logout,
                headers=headers,
                verify=False,
                timeout=30)
            response.raise_for_status()  # Verificar si hay errores en la respuesta
            logging.info("Desconexión exitosa API.")
            self._session_id = None
        except requests.exceptions.HTTPError as errh:
            logging.error("Error HTTP: %s", errh)
        except requests.exceptions.ConnectionError as errc:
            logging.error("Error de conexión API: %s", errc)
        except requests.exceptions.Timeout as errt:
            logging.error("Timeout del request API: %s", errt)
        except requests.exceptions.RequestException as err:
            logging.error("Error en la solicitud API: %s", err)
        
    
    # funcion que realiza una peticion GET al endpoint pasada por param
    # retorna el status y obserror
    def send_get_api(self, endpoint): 
        # obtengo url, endpoint (juntos) y el header con el id session de la conexion realizada
        url_endpoint, headers = self.set_endpoint(endpoint)
        
        try:
            response = requests.get(
                url_endpoint,
                headers=headers,
                verify=False,
                timeout=30)
            response.raise_for_status()  # Verificar si hay errores en la respuesta
            logging.info(f"Solicitud GET realizada con EXITO al Endpoint {url_endpoint}")
            response = response.json()
            
        except requests.exceptions.RequestException as err:
            logging.error("Error en la solicitud GET API: %s", err)
            response = []
        finally:
            return response
    
    def send_post_api(self, endpoint,body): 
        # obtengo url, endpoint (juntos) y el header con el id session de la conexion realizada
        url_endpoint, headers = self.set_endpoint(endpoint)
        try:
            response = requests.post(
                url_endpoint,
                json=body,
                headers=headers,
                verify=False,
                timeout=30)
            response.raise_for_status()  # Verificar si hay errores en la respuesta
            logging.info(f"Solicitud POST realizada con EXITO al Endpoint {url_endpoint}")
            
        except requests.exceptions.RequestException as err:
            logging.error("Error en la solicitud POST API: %s", err)
        finally:
            return self.handle_api_response_doc_entry(response)


    def send_patch_api(self, endpoint,body): 
        # obtengo url, endpoint (juntos) y el header con el id session de la conexion realizada
        url_endpoint, headers = self.set_endpoint(endpoint)
        try:
            response = requests.patch(
                url_endpoint,
                json=body,
                headers=headers,
                verify=False,
                timeout=30)
            response.raise_for_status()  # Verificar si hay errores en la respuesta
            logging.info(f"Solicitud PATCH realizada con EXITO al Endpoint {url_endpoint}")
        except requests.exceptions.RequestException as err:
            logging.error("Error en la solicitud POST API: %s", err)            
        # proceso la respuesta del Service Layer
        finally:
            return self.handle_api_response(response)

    
    def handle_api_response(self,post_response):
    
    #Maneja la respuesta de la API y determina el estado y el mensaje de error.
    #Args:
    #    post_response: La respuesta de la solicitud POST a la API.
    #Returns:
    #    tuple: Una tupla que contiene el estado de la transacción y el mensaje de error.
    #        - status (int): El código de estado de la transacción.
    #            - 2: Indica una transacción exitosa (códigos de estado HTTP 200 o 201).
    #            - 3: Indica una transacción fallida 
    #            (cualquier código de estado HTTP diferente a 200 o 201).
    #        - obserror (str): Un mensaje que indica el resultado de la transacción.
    #            - "OK": Indica que la transacción fue exitosa.
    #            - "Error SAP: {status_code} - {error_message}": Un mensaje de error formateado 
    #            que indica el código de estado HTTP y el mensaje de error devuelto por la API.
    
        if post_response.status_code in [200, 201,204]:
            status = 2
            obserror = "OK"
        else:
            status = 3
            # Obtener el valor de "value" del mensaje de error
            response_json = post_response.json()
            error_value = response_json["error"]["message"].get("value", "No se encontró mensaje de error")
            obserror = f"Error SAP: {post_response.status_code} - {error_value}"

        return status, obserror
    
    def handle_api_response_doc_entry(self,post_response):
    #Maneja la respuesta de la API y determina el estado y el mensaje de error.
    #Args:
    #    post_response: La respuesta de la solicitud POST a la API.
    #
    #Returns:
    #    tuple: Una tupla que contiene el estado de la transacción y el mensaje de error.
    #        - status (int): El código de estado de la transacción.
    #            - 2: Indica una transacción exitosa (códigos de estado HTTP 200 o 201).
    #            - 3: Indica una transacción fallida 
    #            (cualquier código de estado HTTP diferente a 200 o 201).
    #        - obserror (str): Un mensaje que indica el resultado de la transacción.
    #            - "OK": Indica que la transacción fue exitosa.
    #            - "Error SAP: {status_code} - {error_message}": Un mensaje de error formateado 
    #            que indica el código de estado HTTP y el mensaje de error devuelto por la API.
    #        - doc_entry (int): Retorna el DocEntry de la generacion de cada documento en SAP.
        response_json = post_response.json()
        doc_entry = 'NULL'
        if post_response.status_code in [200, 201,204]:
            if post_response.status_code == 201:
                doc_entry = response_json["DocEntry"] if "DocEntry" in response_json else response_json["JdtNum"] if "JdtNum" in response_json else 'NULL'
            status = 2
            obserror = "OK"
        else:
            status = 3
            # Obtener el valor de "value" del mensaje de error
            error_value = response_json["error"]["message"].get("value", "No se encontró mensaje de error")
            obserror = f"Error SAP: {post_response.status_code} - {error_value}"

        return status, obserror, doc_entry
    # funcion que setea el endpoint y los headers para las requests
    def set_endpoint(self, endpoint):
        url_endpoint = f"{self.__url}{endpoint}"
        headers = {
                    "Cookie": f"B1SESSION={self._session_id}; ROUTEID=.node1",
                    'Content-Type': 'application/json'
                  }
        return url_endpoint, headers