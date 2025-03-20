from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class AMBIENTE(models.Model):
    id_ambiente = models.AutoField(primary_key=True)
    nombre_ambiente = models.CharField (max_length=100)
    descripcion_ambiente = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user_create = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    
    def __str__(self):
        return self.nombre_ambiente + ' by -' + self.user_create.username + ' Creado el:' + self.fecha_creacion.strftime("%d/%m/%Y %H:%M")
        #return f"{self.nombre_ambiente} Creado por: {self.user_create.username} (Creado el: {self.fecha_creacion.strftime("%d/%m/%Y %H:%M")})"

class Bitacora(models.Model):
    TIPO_ACCION = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
        ('VIEW', 'Visualizar'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    tipo_accion = models.CharField(max_length=10, choices=TIPO_ACCION)
    tabla_afectada = models.CharField(max_length=50)
    descripcion = models.TextField()

    class Meta:
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.usuario} - {self.tipo_accion} - {self.fecha_hora}"

class Perfil(models.Model):
    id_perfil = models.AutoField(primary_key=True)
    nombre_perfil = models.CharField(max_length=100)
    descripcion_perfil = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user_create = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, verbose_name='Creado por')

    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfiles'
        ordering = ['nombre_perfil']

    def __str__(self):
        if self.user_create:
            return f"{self.nombre_perfil} (Creado por: {self.user_create.username} el: {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')})"
        return f"{self.nombre_perfil} (Creado el: {self.fecha_creacion.strftime('%d/%m/%Y %H:%M')})"

class UsuarioExtendido(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.perfil.nombre_perfil if self.perfil else 'Sin perfil'}"

class CLOUD(models.Model):
    id_cloud = models.AutoField(primary_key=True)
    nombre_cloud = models.CharField(max_length=100)
    siglas_cloud = models.CharField(max_length=10)
    ambientes = models.ManyToManyField(AMBIENTE, related_name='clouds')
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'CLOUD'
        ordering = ['nombre_cloud']

    def __str__(self):
        return f"{self.siglas_cloud} - {self.nombre_cloud}"

class SOLICITANTE(models.Model):
    id_solicitante = models.AutoField(primary_key=True)
    nombre_solicitante = models.CharField(max_length=100)
    puesto_solicitante = models.CharField(max_length=100)
    email_solicitante = models.EmailField()
    tel_solicitante = models.CharField(max_length=20)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_solicitante

class GERENCIA(models.Model):
    id_gerencia = models.AutoField(primary_key=True)
    nombre_gerencia = models.CharField(max_length=100)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_gerencia

class PUESTO(models.Model):
    id_puesto = models.AutoField(primary_key=True)
    nombre_puesto = models.CharField(max_length=100)
    descripcion_puesto = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE, related_name='puestos_creados')
    
    def __str__(self):
        return self.nombre_puesto
    
    class Meta:
        verbose_name = 'Puesto'
        verbose_name_plural = 'Puestos'
        ordering = ['nombre_puesto']
      