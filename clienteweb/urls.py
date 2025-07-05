from django.urls import path
from . import views


urlpatterns = [
    path('orden_mantenimiento/', views.orden_mantenimiento_view, name='orden_mantenimiento'),
    path('pagina_principal/', views.pagina_principal_view, name='pagina_principal'),
    path('equipos/', views.equipos_view, name="equipos"),
    path('proceso_aprobacion/', views.proceso_aprobacion_view, name="proceso_aprobacion"),
    path('api/equipos/', views.api_get_equipos, name='api_equipos'),
    path('api/tipos_om/', views.api_get_tipos_om, name='api_tipos_om'),
    path('api/talleres/', views.api_get_talleres, name='api_talleres'),
]