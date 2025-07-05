from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# creacion del modelo Usuario
class Usuario(AbstractUser):
    cod_empleado = models.IntegerField(blank=True, null=True)

# creacion del modelo Tarea_Mantenimiento
class Tarea_Mantenimiento(models.Model):
    nro_tarea = models.IntegerField()
    nro_om = models.IntegerField()
    equipo = models.CharField(max_length=100)
    desc_equipo = models.TextField()
    desc_tarea = models.TextField()
    fecha_inicio = models.DateTimeField(auto_now_add=True)
    fecha_fin = models.DateTimeField(blank=True, null=True)
    horas_trabajadas_totales = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    salario_empleado = models.DecimalField(max_digits=20,decimal_places=2,null=True, blank=True)
    estado = models.IntegerField() # 1 = EN PROCESO, 2 = EN PAUSA, 3 = FINALIZADA
    id_tarea_om = models.IntegerField(null=True) # id de la tarea dentro de la OM
    usuario = models.ForeignKey(Usuario,null=True, on_delete=models.CASCADE)

    @classmethod
    def existe_tarea_asignada_a_usuario(cls,usuario):
        return cls.objects.filter(usuario=usuario, estado=1).exists()
    
class Tarea_Registro(models.Model):
    tarea = models.ForeignKey(Tarea_Mantenimiento, on_delete=models.DO_NOTHING,related_name='pausas')
    usuario = models.ForeignKey(Usuario, null=True, on_delete=models.DO_NOTHING)
    fecha_inicio_pausa = models.DateTimeField(blank=True, null=True)
    fecha_fin_pausa = models.DateTimeField(blank=True, null=True)

    @property
    def horas_trabajadas(self):
        return (self.fecha_fin_pausa - self.fecha_inicio_pausa).total_seconds() / 3600
        