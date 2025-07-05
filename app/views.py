from .modulos.Api_SL import Api_SL
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout # Renombrar para evitar conflicto
from django.contrib.auth.decorators import login_required # Para proteger otras vistas
from .modulos.Api_SL import Api_SL
from .models import Usuario, Tarea_Mantenimiento as Tarea, Tarea_Registro

def login(request): 
    error_message = None
    if request.method == 'POST':
        username_form = request.POST.get('username')
        password_form = request.POST.get('password')

        u = Usuario.objects.get(username=username_form)    

        user = authenticate(request, username=username_form, password=password_form)
        print(user)
        if user is not None:
            auth_login(request, user)
            # Redirigir a una página de "bienvenida" o a la de tareas
            # Si tienes una URL para un panel de admin, redirige allí.
            # Por ejemplo, si 'tareas' es la página principal después del login:
            return redirect('pagina_principal') 
        else:
            error_message = "Usuario o contraseña incorrectos."
            
    return render(request, 'login.html', {'error_message': error_message})


@login_required()
def listar_tareas(request):
    if request.method == 'GET':
        if Tarea.existe_tarea_asignada_a_usuario(request.user):
            tarea_asignada = Tarea.objects.filter(usuario=request.user).first()
            
            return render(request, "tarea_asignada.html",{
                'tarea': tarea_asignada,
            })
        else:
            config_data = {
                "login_credentials": {
                "CompanyDB": {
                  "TDU": "TEST_TDU",
                  "COD": "TEST_CODYLSA",
                  "DYL": "TEST_DYLASA",
                  "MAL": "TEST_MALARGUE",
                 # "CIM": "TEST_CIMSA"
                  "CIM": "CIMSA"
                 },
                "Password": "Initial0!", 
                #"Password": "1234", 
                "UserName": "manager"
              }
            }
            # Hacer la petición GET a la API
            api_sl = Api_SL("https://192.168.100.105:50000/b1s/v1")
            api_sl.connect_api("CIM",config_data)

            nro_empleado = request.user.cod_empleado 
            # haz la consulta a la API de SAP para obtener los nro de responsable que no esten vacios sin utilizar nroempleado
            #url_get = f"/sml.svc/CV_TAREAS?$filter=Nro_Responsable eq '{nro_empleado}' and Estado_Tarea eq 1"

            url_get = f"/sml.svc/CV_TAREAS?$filter=Nro_Responsable eq '{nro_empleado}'"

            res = api_sl.send_get_api(url_get)

            if res['value'] != []:
            #    nro_om = res['value'][0]['DocEntry']
                nombre_mecanico = res['value'][0]['Responsable']
                om_procesadas = procesar_om(res['value'])

                return render(request, "tareas.html", 
                              {
                                'res': om_procesadas,
                                "usuario": nombre_mecanico
                              }
                          )
            return HttpResponse("Sin tareas pendientes de iniciar")

@login_required()
def enviar_mails(request):
    return render(request, "enviar_mails.html")

def procesar_om(ordenes_mantenimiento):

    om_procesadas = {}

    for om in ordenes_mantenimiento:
        if om['Nro_OM'] not in om_procesadas:
            om_procesadas[om['Nro_OM']] = {
                'equipo': om['Equipo'],
                'desc_equipo': om['Desc__Equipo'],
                'tareas': []
            }
        om_procesadas[om['Nro_OM']]['tareas'].append({
            'nro_tarea': om['Nro_Tarea'],
            'desc_tarea': om['Desc__Tarea'],
            'estado': om['Estado_Tarea']
        })
    return om_procesadas


def crear_tarea(request):
    if request.method == 'GET':
        return redirect('tareas')
    else:
        # cuando inicio una tarea, puede suceder que ya exista el registro dentro de la bd
        # para ello, en caso de que sea asi, no se crea una nueva tarea, sino que se actualiza la existente
        
        #if Tarea.objects.filter(nro_tarea = request.POST.get('nro_tarea')).exists():
            # Creacion de la tarea dentro de la base de datos
        tarea_creada = Tarea.objects.create(   
            nro_tarea=request.POST.get('nro_tarea'),
            nro_om = request.POST.get('nro_om'),
            equipo=request.POST.get('equipo'),
            desc_equipo=request.POST.get('desc_equipo'),
            desc_tarea=request.POST.get('desc_tarea'),  
            estado= 1, 
            usuario=request.user
        )

        return redirect('tareas')

def actualizar_tarea(request):
    if request.method == 'GET':
        return redirect('tareas')   
    else:   
        # Actualizar la tarea dentro de la base de datos
        nro_tarea_get = request.POST.get('nro_tarea')
        try:
            tarea = Tarea.objects.get(nro_tarea=nro_tarea_get, usuario=request.user)
            if request.POST.get('accion') == 'pausar':
                tarea.estado = 2
                # se registra la pausa de la tarea dentro de la bd
                tarea = registrar_pausa_tarea(tarea)
                
            
            elif request.POST.get('accion') == 'finalizar':
                tarea.estado = 3
            
            tarea.usuario = None  # desaigno la tarea al usuario


            tarea.save()
            return redirect('tareas')
        except Tarea.DoesNotExist:
            return HttpResponse("Tarea no encontrada o no asignada a este usuario.")



def logout(request):
    auth_logout(request)
    return redirect('login')  

def registrar_pausa_tarea(tarea):
    #Tarea_Registro.objects.create(
    #    tarea=tarea,
    #    usuario=request.user,
    #    fecha_inicio_pausa=tarea.fecha_inicio
    #    fecha_fin_pausa=None  # Se deja en None al iniciar la pausa
    #)
    
    # por funcionamiento de SAP B1, primero, es necesario crear el asiento contable de la pausa
    config_data = {
                "login_credentials": {
                "CompanyDB": {
                  "TDU": "TEST_TDU",
                  "COD": "TEST_CODYLSA",
                  "DYL": "TEST_DYLASA",
                  "MAL": "TEST_MALARGUE",
                 # "CIM": "TEST_CIMSA"
                  "CIM": "TEST_CIMSA"
                 },
                "Password": "1234", 
                #"Password": "1234", 
                "UserName": "manager"
              }
            }
            # Hacer la petición GET a la API
    api_sl = Api_SL("https://192.168.100.105:50000/b1s/v1")
    api_sl.connect_api("CIM",config_data)