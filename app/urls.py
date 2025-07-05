from django.urls import path
from . import views


urlpatterns = [
    path('', views.login, name="login"),
    path('tareas/', views.listar_tareas, name="tareas"),
    path('tareas/crear/', views.crear_tarea, name="crear_tarea"),
    path('tareas/actualizar/', views.actualizar_tarea, name="actualizar_tarea"), 
    path('envio_mails/', views.enviar_mails, name="enviar_mails"),
    path('logout/', views.logout, name="logout"),
]