import requests
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os
import urllib3 # Para desactivar advertencias de SSL si es necesario

# --- 1. CONFIGURACIÓN ---

# Service Layer Details
# ¡¡IMPORTANTE!! Usa HTTPS. El puerto por defecto es 50000. Verifica tu URL.
SL_BASE_URL = 'https://181.119.121.70:50000/b1s/v1/' # ¡Asegúrate que sea la URL correcta!
# El nombre de la compañía como aparece en la pantalla de login de SAP B1 / Service Layer
SL_COMPANY_DB = 'TEST_TDU' # ¡Verifica que sea el nombre exacto de la sociedad en SAP!
SL_USER = 'manager' # Usuario de SAP B1 con licencia para Service Layer
SL_PASSWORD = '1234' # Contraseña del usuario SAP B1
# Desactivar advertencias si usas certificados autofirmados (NO RECOMENDADO para producción)
DISABLE_SSL_WARNINGS = True
# Si tienes un certificado válido y confiable en tu sistema, pon False.
# Si usas un certificado específico: VERIFY_SSL = '/ruta/a/tu/certificado.pem'
VERIFY_SSL = False # Poner True o ruta al certificado en producción

# OData Query Parameters (Basado en tu SQL)
# Campos a seleccionar (¡verifica si CurrentAccountBalance es el correcto para "Balance"!)
SELECT_FIELDS = 'CardCode,CardName,CurrentAccountBalance'
# Filtro: Tipo Cliente ('C') y Saldo > 0
FILTER_QUERY = "CardType eq 'cCustomer' and CurrentAccountBalance gt 0"
# Ordenar por nombre
ORDER_BY = 'CardName asc'

# Excel File Details
EXCEL_FILENAME = 'reporte_sap_b1_sl.xlsx'
EXCEL_SHEET_NAME = 'ClientesConSaldo'

# Email Details (Igual que antes)
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SMTP_USER = 'sap@codylsa.com'
SMTP_PASSWORD = 'qdny kwli okel tvku'
SENDER_EMAIL = 'sap@codylsa.com'
RECEIVER_EMAIL = 'sferreiros@codylsa.com'
EMAIL_SUBJECT = 'Reporte SAP B1 (Service Layer) - Clientes con Saldo'
EMAIL_BODY = 'Adjunto se encuentra el reporte de clientes con saldo generado desde SAP B1.'

# --- Helper para desactivar warnings SSL ---
if DISABLE_SSL_WARNINGS:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_data_from_service_layer(sl_config, odata_params):
    """Conecta al Service Layer, obtiene datos paginados y devuelve un DataFrame."""
    login_payload = {
        "CompanyDB": sl_config['company_db'],
        "UserName": sl_config['user'],
        "Password": sl_config['password']
    }

    session = requests.Session()
    session.verify = sl_config['verify_ssl'] # Manejo de verificación SSL

    all_data = []
    next_link = None

    try:
        print("Iniciando sesión en Service Layer...")
        login_resp = session.post(sl_config['base_url'] + 'Login', json=login_payload)
        login_resp.raise_for_status() # Lanza excepción si hay error HTTP (4xx o 5xx)
        print("Login exitoso.")

        # Construir URL inicial
        query_url = f"{sl_config['base_url']}BusinessPartners?$select={odata_params['select']}&$filter={odata_params['filter']}&$orderby={odata_params['orderby']}"
        next_link = query_url # Asignar para iniciar el bucle

        print("Obteniendo datos de BusinessPartners...")
        while next_link:
            print(f"  Consultando: {next_link}")
            data_resp = session.get(next_link)
            data_resp.raise_for_status()
            response_data = data_resp.json()

            all_data.extend(response_data.get('value', []))

            # Verificar si hay más páginas
            next_link = response_data.get('odata.nextLink')
            if next_link:
                # Service Layer a veces devuelve el nextLink como ruta relativa, hacerlo absoluto
                if not next_link.startswith('http'):
                   # Extraer la base de la URL de SL (hasta /v1/)
                   base = sl_config['base_url'].split('/b1s/v1/')[0] + '/b1s/v1/'
                   next_link = base + next_link
                print("  Paginación detectada, obteniendo siguiente lote...")
            else:
                print("  No hay más páginas.")

        print(f"Datos obtenidos. Total de registros: {len(all_data)}")
        if not all_data:
            print("La consulta no devolvió resultados.")
            return None

        # Convertir a DataFrame
        df = pd.DataFrame(all_data)
        # Seleccionar y reordenar columnas si es necesario para que coincida con SELECT_FIELDS
        # Los nombres en el DataFrame serán los que devuelve Service Layer
        selected_columns = odata_params['select'].split(',')
        df = df[selected_columns] # Asegura que solo estén las columnas pedidas y en ese orden
        print("Datos convertidos a DataFrame.")
        return df

    except requests.exceptions.RequestException as e:
        print(f"Error durante la comunicación con Service Layer: {e}")
        # Imprimir más detalles si la respuesta está disponible
        if e.response is not None:
            print(f"Respuesta del servidor: {e.response.status_code} - {e.response.text}")
        return None
    except Exception as e:
        print(f"Error inesperado en get_data_from_service_layer: {e}")
        return None
    finally:
        # Siempre intentar cerrar sesión si la sesión se estableció
        if session and 'B1SESSION' in session.cookies:
            try:
                print("Cerrando sesión de Service Layer...")
                logout_resp = session.post(sl_config['base_url'] + 'Logout')
                if logout_resp.status_code == 204:
                    print("Logout exitoso.")
                else:
                    # No lanzar excepción aquí, solo informar
                    print(f"Problema al cerrar sesión: {logout_resp.status_code} - {logout_resp.text}")
            except requests.exceptions.RequestException as e_logout:
                 print(f"Error al intentar cerrar sesión: {e_logout}")
        print("Proceso de obtención de datos finalizado.")


def save_to_excel(dataframe, excel_path, sheet_name):
    """Guarda un DataFrame en un archivo Excel."""
    if dataframe is not None and not dataframe.empty:
        try:
            print(f"Guardando DataFrame en {excel_path}...")
            dataframe.to_excel(excel_path, sheet_name=sheet_name, index=False, engine='openpyxl')
            print("Archivo Excel guardado exitosamente.")
            return True
        except Exception as e:
            print(f"Error al guardar el archivo Excel: {e}")
            return False
    else:
        print("No hay datos para guardar en Excel.")
        return False

# La función send_email_with_attachment es la misma que en el script anterior
# (No la repito aquí por brevedad, asegúrate de tenerla en tu script)
def send_email_with_attachment(smtp_config, mail_content, attachment_path):
    """Envía un correo electrónico con un archivo adjunto."""
    try:
        print(f"Preparando email para: {mail_content['receiver']}")
        msg = MIMEMultipart()
        msg['From'] = mail_content['sender']
        # Manejar tanto un solo destinatario (str) como múltiples (list)
        if isinstance(mail_content['receiver'], list):
             msg['To'] = ", ".join(mail_content['receiver'])
             receiver_list = mail_content['receiver']
        else:
             msg['To'] = mail_content['receiver']
             receiver_list = [mail_content['receiver']]

        msg['Subject'] = mail_content['subject']

        msg.attach(MIMEText(mail_content['body'], 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            print(f"Adjuntando archivo: {attachment_path}")
            part = MIMEBase('application', 'octet-stream')
            with open(attachment_path, 'rb') as attachment:
                part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename={os.path.basename(attachment_path)}',
            )
            msg.attach(part)
            print("Archivo adjuntado.")
        else:
            print(f"Advertencia: El archivo adjunto {attachment_path} no fue encontrado o no se proporcionó.")
            # Decidir si enviar el correo sin adjunto o no
            # return False # Descomentar si no se quiere enviar sin adjunto

        print(f"Conectando al servidor SMTP: {smtp_config['server']}:{smtp_config['port']}")
        # Usar SMTP_SSL si el puerto es 465, de lo contrario usar SMTP y starttls()
        if smtp_config['port'] == 465:
             server = smtplib.SMTP_SSL(smtp_config['server'], smtp_config['port'])
        else:
             server = smtplib.SMTP(smtp_config['server'], smtp_config['port'])
             server.starttls() # Usar TLS para puertos como 587

        server.login(smtp_config['user'], smtp_config['password'])
        print("Login SMTP exitoso.")
        server.sendmail(mail_content['sender'], receiver_list, msg.as_string())
        print("Email enviado exitosamente.")
        server.quit()
        print("Conexión SMTP cerrada.")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error de autenticación SMTP: {e}. Verifica usuario/contraseña o configuración de 'aplicaciones menos seguras'/contraseñas de aplicación.")
        return False
    except Exception as e:
        print(f"Error al enviar el email: {e}")
        return False


if __name__ == "__main__":
    sl_connection_config = {
        'base_url': SL_BASE_URL,
        'company_db': SL_COMPANY_DB,
        'user': SL_USER,
        'password': SL_PASSWORD,
        'verify_ssl': VERIFY_SSL
    }

    odata_query_details = {
        'select': SELECT_FIELDS,
        'filter': FILTER_QUERY,
        'orderby': ORDER_BY
    }

    # 1. Obtener datos desde Service Layer
    dataframe_resultado = get_data_from_service_layer(sl_connection_config, odata_query_details)

    # 2. Guardar en Excel si se obtuvieron datos
    excel_generado = False
    if dataframe_resultado is not None:
        excel_generado = save_to_excel(dataframe_resultado, EXCEL_FILENAME, EXCEL_SHEET_NAME)

    # 3. Si el Excel se generó, enviar por correo
    if excel_generado:
        smtp_details = {
            'server': SMTP_SERVER,
            'port': SMTP_PORT,
            'user': SMTP_USER,
            'password': SMTP_PASSWORD
        }
        email_content = {
            'sender': SENDER_EMAIL,
            'receiver': RECEIVER_EMAIL,
            'subject': EMAIL_SUBJECT,
            'body': EMAIL_BODY
        }
        email_enviado = send_email_with_attachment(
            smtp_config=smtp_details,
            mail_content=email_content,
            attachment_path=EXCEL_FILENAME
        )
        # Opcional: Eliminar el archivo Excel después de enviarlo si se envió correctamente
        # if email_enviado and os.path.exists(EXCEL_FILENAME):
        #     os.remove(EXCEL_FILENAME)
        #     print(f"Archivo {EXCEL_FILENAME} eliminado.")
    else:
        print("No se generó el archivo Excel o no se obtuvieron datos, por lo tanto no se enviará ningún correo.")