
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login as auth_login # Renombrar para evitar conflicto
from django.contrib.auth.decorators import login_required # Para proteger otras vistas
from .logica_statusdoc import fetch_sap_status_docs

from django.http import JsonResponse
from . import sap_service  # <-- 1. Importamos nuestro nuevo servicio

    

#def login(request):
#    return HttpResponse("IMPLEMENTAR LOGIN")
def api_get_tipos_om(request):
    """
    API interna para obtener los Tipos de OM desde SAP.
    """
    endpoint = "https://181.119.121.70:50000/b1s/v1/VID_MTTIPOM?$select=Name"
    tipos_om = sap_service.get_sap_data(endpoint)
    return JsonResponse(tipos_om, safe=False)


def api_get_talleres(request):
    """
    API interna para obtener los Talleres desde SAP.
    """
    endpoint = "https://181.119.121.70:50000/b1s/v1/VID_MTTALLER?$select=Name"
    talleres = sap_service.get_sap_data(endpoint)
    return JsonResponse(talleres, safe=False)


def orden_mantenimiento_view(request):
    return render(request, 'orden_mantenimiento.html')

def api_get_equipos(request):
    """
    API interna para obtener TODOS los equipos desde SAP.
    Ajusta el endpoint y los filtros según sea necesario.
    """
    # Debes ajustar este endpoint. Probablemente sea la tabla de Items (OITM)
    # con un filtro por grupo de item si es que tienes uno para "Equipos".
    # Usamos $select para traer solo los campos necesarios.
    endpoint = "https://181.119.121.70:50000/b1s/v1/VID_MTEQUIPOS?$select=Code,Name" 
    equipos = sap_service.get_sap_data(endpoint)
    return JsonResponse(equipos, safe=False)

def pagina_principal_view(request):
    return render(request, 'pagina_principal.html')

def proceso_aprobacion_view(request):
    return render(request, 'proceso_aprobacion.html')

# Reemplaza la antigua equipos_view por esta en tu app/views.py

# Reemplaza la equipos_view en tu app/views.py por esta versión

def equipos_view(request):
    context = {
        'equipo': None,
        'busqueda_realizada': False,
    }
    
    equipo_id = request.GET.get('id')
    
    if equipo_id:
        context['busqueda_realizada'] = True
        
        # --- CAMBIO IMPORTANTE AQUÍ ---
        # En lugar de ('codigo'), usamos el filtro $filter=Code eq 'codigo'
        # Esto es más robusto y es el estándar de OData para filtrar.
        endpoint_detalles = f"https://181.119.121.70:50000/b1s/v1/VID_MTEQUIPOS?$filter=Code eq '{equipo_id}'"
        
        print(f">>> Consultando detalles para el equipo con filtro: {equipo_id}")
        print(f">>> Nueva URL: {endpoint_detalles}")
        
        datos_de_sap_lista = sap_service.get_sap_data(endpoint_detalles)
        
        # La respuesta de un filtro siempre es una lista, aunque solo tenga un resultado.
        # Debemos verificar si la lista no está vacía y tomar el primer elemento.
        if datos_de_sap_lista and len(datos_de_sap_lista) > 0:
            # Tomamos el primer (y único) resultado de la lista
            context['equipo'] = datos_de_sap_lista[0]
            print(">>> ¡Éxito! Datos encontrados y pasados a la plantilla.")
            print(context['equipo']) # Imprimimos los datos para ver qué nos trae SAP
        else:
            print(f"!!! No se encontraron datos en SAP para el equipo: {equipo_id}")
            
    return render(request, 'equipos.html', context)

def proceso_aprobacion_view(request):
    """
    Obtiene los docs, agrupa las etapas de aprobación completas en una lista 'Historial'
    y elimina los duplicados.
    """
    estado_filtro = request.GET.get('estado', 'Pendiente')
    
    # 1. Obtenemos todos los registros de SAP (incluyendo una fila por cada etapa)
    documentos_desde_sap = fetch_sap_status_docs(estado=estado_filtro)

    # 2. Procesamos la lista para agrupar las etapas por documento
    documentos_agrupados = {}
    
    if documentos_desde_sap:
        for etapa_doc in documentos_desde_sap:
            # Clave única para cada documento
            clave = (etapa_doc.get('Empresa'), etapa_doc.get('Ndeborrador'))

            # Si es la primera vez que vemos este documento...
            if clave not in documentos_agrupados:
                # Lo guardamos y creamos su lista 'Historial', añadiendo el objeto de etapa completo.
                documentos_agrupados[clave] = etapa_doc
                documentos_agrupados[clave]['Historial'] = [etapa_doc]
            # Si el documento ya existe...
            else:
                # Simplemente añadimos el objeto de etapa completo a su lista 'Historial' existente.
                documentos_agrupados[clave]['Historial'].append(etapa_doc)

    # Convertimos el diccionario de nuevo a una lista para la plantilla
    documentos_finales = list(documentos_agrupados.values())

    # 3. Creamos el contexto con la estructura de datos correcta
    context = {
        'documentos': documentos_finales,
        'estado_actual': estado_filtro
    }
    
    return render(request, 'proceso_aprobacion.html', context)