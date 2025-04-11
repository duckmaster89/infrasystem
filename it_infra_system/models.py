from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError

# Create your models here.
class AMBIENTE(models.Model):
    id_ambiente = models.AutoField(primary_key=True)
    nombre_ambiente = models.CharField (max_length=100)
    descripcion_ambiente = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user_create = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.nombre_ambiente

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
    perfiles = models.ManyToManyField(Perfil, related_name='usuarios', blank=True)

    def __str__(self):
        perfiles_str = ', '.join([p.nombre_perfil for p in self.perfiles.all()])
        return f"{self.user.username} - {perfiles_str if perfiles_str else 'Sin perfiles'}"

    def tiene_perfil(self, nombre_perfil):
        return self.perfiles.filter(nombre_perfil=nombre_perfil).exists()

    def es_administrador(self):
        return self.perfiles.filter(nombre_perfil='Administrador').exists()

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
    id_solicitante = models.IntegerField(primary_key=True)
    nombre_solicitante = models.CharField(max_length=100)
    puesto_solicitante = models.CharField(max_length=100, blank=True, null=True)
    email_solicitante = models.EmailField()
    tel_solicitante = models.CharField(max_length=20)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    puesto = models.ForeignKey('PUESTO', on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitantes')
    gerencia = models.ForeignKey('GERENCIA', on_delete=models.SET_NULL, null=True, blank=True, related_name='solicitantes')

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

class VLAN(models.Model):
    id_vlan = models.AutoField(primary_key=True)
    numero_vlan = models.IntegerField(help_text="Número de VLAN (1-4094)")
    barra_vlan = models.IntegerField(help_text="Máscara de subred en notación CIDR (0-32)")
    segmento_vlan = models.GenericIPAddressField(protocol='IPv4', help_text="Dirección IPv4 del segmento")
    uso_red = models.ForeignKey('USO_RED', on_delete=models.SET_NULL, null=True, blank=True)
    cloud = models.ForeignKey(CLOUD, on_delete=models.CASCADE, related_name='vlans', help_text="Cloud al que pertenece la VLAN")
    ambiente = models.ForeignKey(AMBIENTE, on_delete=models.CASCADE, related_name='vlans', null=True, help_text="Ambiente al que pertenece la VLAN")
    proyecto = models.ForeignKey('PROYECTO', on_delete=models.SET_NULL, null=True, blank=True, help_text="Proyecto asociado a la VLAN")
    red = models.ForeignKey('RED', on_delete=models.SET_NULL, null=True, blank=True)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'VLAN'
        verbose_name_plural = 'VLANs'
        ordering = ['numero_vlan']
        unique_together = ['numero_vlan', 'cloud']  # Asegura que el número de VLAN sea único por cloud

    def __str__(self):
        return f"VLAN {self.numero_vlan} - {self.segmento_vlan}/{self.barra_vlan}"

    def clean(self):
        # Validar el rango del número de VLAN
        if self.numero_vlan < 1 or self.numero_vlan > 4094:
            raise ValidationError({'numero_vlan': 'El número de VLAN debe estar entre 1 y 4094'})
        
        # Validar el rango de la barra VLAN
        if self.barra_vlan < 0 or self.barra_vlan > 32:
            raise ValidationError({'barra_vlan': 'La máscara CIDR debe estar entre 0 y 32'})
        
        # Validar que ambiente y cloud sean proporcionados
        if not self.ambiente:
            raise ValidationError({'ambiente': 'El ambiente es obligatorio'})

class PROYECTO(models.Model):
    id_proyecto = models.AutoField(primary_key=True)
    nombre_proyecto = models.CharField(max_length=100)
    fecha_solicitud = models.DateField()
    fecha_asignacion = models.DateField(null=True, blank=True)
    solicitante = models.ForeignKey(SOLICITANTE, on_delete=models.SET_NULL, null=True, blank=True)
    arquitecto = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='proyectos_arquitecto')
    uso_red = models.ForeignKey('USO_RED', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Uso de Red')
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_proyecto

    class Meta:
        db_table = 'proyecto'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'      

class STATUS_PROYECTO(models.Model):
    id_status = models.AutoField(primary_key=True)
    nombre_status = models.CharField(max_length=100)
    descripcion_status = models.TextField()
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_status

    class Meta:
        db_table = 'status_proyecto'
        verbose_name = 'Estado de Proyecto'
        verbose_name_plural = 'Estados de Proyecto'
        ordering = ['nombre_status']      

class PAIS(models.Model):
    id_pais = models.AutoField(primary_key=True)
    nombre_pais = models.CharField(max_length=100)
    abreviatura_pais = models.CharField(max_length=3)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_pais

    class Meta:
        db_table = 'pais'
        verbose_name = 'País'
        verbose_name_plural = 'Países'
        ordering = ['nombre_pais']      

class RED(models.Model):
    id_red = models.AutoField(primary_key=True)
    nombre_red = models.CharField(max_length=100)
    descripcion_red = models.TextField(null=True, blank=True)
    segmento_red = models.CharField(max_length=15, null=True, blank=True, default='0.0.0.0')
    barra_red = models.IntegerField(null=True, blank=True, default=24)
    ip_inicio = models.CharField(max_length=15, null=True, blank=True)
    ip_fin = models.CharField(max_length=15, null=True, blank=True)
    uso_red = models.ForeignKey('USO_RED', on_delete=models.SET_NULL, null=True, blank=True)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE, related_name='redes_creadas')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user_update = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='redes_actualizadas')
    date_update = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombre_red} - {self.segmento_red}/{self.barra_red}"

    class Meta:
        db_table = 'RED'
        verbose_name = 'Red'
        verbose_name_plural = 'Redes'

class USO_RED(models.Model):
    id_uso_red = models.AutoField(primary_key=True)
    nombre_uso = models.CharField(max_length=100)
    descripcion_uso = models.TextField()
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_uso

    class Meta:
        verbose_name = 'Uso de Red'
        verbose_name_plural = 'Usos de Red'
        ordering = ['nombre_uso']      

class CONTROL_VLAN(models.Model):
    id_control_vlan = models.AutoField(primary_key=True)
    nombre_tabla_vlan = models.CharField(max_length=100)
    uso_red = models.ForeignKey('USO_RED', on_delete=models.CASCADE, related_name='control_vlans')
    proyecto = models.ForeignKey('PROYECTO', on_delete=models.CASCADE, related_name='control_vlans', null=True, blank=True)
    rango_ips_disponibles = models.CharField(max_length=100, blank=True, null=True)
    user_create = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'CONTROL_VLAN'
        verbose_name = 'Control de VLAN'
        verbose_name_plural = 'Controles de VLAN'
        ordering = ['nombre_tabla_vlan']

    def __str__(self):
        return f"{self.nombre_tabla_vlan} - {self.uso_red.nombre_uso} - {self.proyecto.nombre_proyecto if self.proyecto else 'Uso Común'}"

class VLAN_IP(models.Model):
    id_vlan_ip = models.AutoField(primary_key=True)
    vlan = models.ForeignKey(VLAN, on_delete=models.CASCADE, related_name='ips')
    ip = models.GenericIPAddressField(unique=True)
    hostname = models.CharField(max_length=100, null=True, blank=True)
    usuario = models.CharField(max_length=100, null=True, blank=True)
    fecha_solicitud = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='disponible')

    class Meta:
        db_table = 'vlan_ip'
        verbose_name = 'IP de VLAN'
        verbose_name_plural = 'IPs de VLAN'

    def __str__(self):
        return f"{self.ip} - {self.vlan.numero_vlan}"      

class CPU(models.Model):
    cpu_id = models.AutoField(primary_key=True)
    core_cpu = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'CPU'
        verbose_name = 'CPU'
        verbose_name_plural = 'CPUs'

    def __str__(self):
        return f"CPU {self.cpu_id} - {self.core_cpu} cores"      

class VTI(models.Model):
    vti_id = models.AutoField(primary_key=True)
    nombre_vti = models.CharField(max_length=100)
    siglas = models.CharField(max_length=10, blank=True)
    descripcion = models.TextField(blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    user_create = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'VTI'
        verbose_name_plural = 'VTIs'
        ordering = ['vti_id']

    def __str__(self):
        return f"{self.nombre_vti} ({self.siglas})"      