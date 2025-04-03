from django.forms import ModelForm
from .models import AMBIENTE, SOLICITANTE, GERENCIA, PUESTO, VLAN, PROYECTO, STATUS_PROYECTO, Perfil, User, PAIS, RED, USO_RED
from django import forms


class AmbienteForm(ModelForm):
    class Meta:
        model = AMBIENTE
        fields = ['nombre_ambiente', 'descripcion_ambiente']

class SolicitanteForm(forms.ModelForm):
    class Meta:
        model = SOLICITANTE
        fields = ['nombre_solicitante', 'email_solicitante', 'tel_solicitante', 'puesto', 'gerencia']
        labels = {
            'nombre_solicitante': 'Nombre del Solicitante',
            'email_solicitante': 'Correo Electrónico',
            'tel_solicitante': 'Teléfono',
            'puesto': 'Puesto',
            'gerencia': 'Gerencia'
        }
        widgets = {
            'nombre_solicitante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre completo'}),
            'email_solicitante': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'ejemplo@claro.com.gt'}),
            'tel_solicitante': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el número telefónico'}),
            'puesto': forms.Select(attrs={'class': 'form-control'}),
            'gerencia': forms.Select(attrs={'class': 'form-control'})
        }

class GerenciaForm(forms.ModelForm):
    class Meta:
        model = GERENCIA
        fields = ['nombre_gerencia']
        labels = {
            'nombre_gerencia': 'Nombre de la Gerencia'
        }
        widgets = {
            'nombre_gerencia': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de la gerencia'})
        }

class PuestoForm(forms.ModelForm):
    class Meta:
        model = PUESTO
        fields = ['nombre_puesto', 'descripcion_puesto']
        widgets = {
            'nombre_puesto': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del puesto'}),
            'descripcion_puesto': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del puesto', 'rows': 3}),
        }
        labels = {
            'nombre_puesto': 'Nombre del Puesto',
            'descripcion_puesto': 'Descripción',
        }

class VLANForm(forms.ModelForm):
    class Meta:
        model = VLAN
        fields = ['numero_vlan', 'segmento_vlan', 'barra_vlan', 'uso_red', 'cloud', 'ambiente', 'proyecto']
        labels = {
            'numero_vlan': 'Número de VLAN',
            'segmento_vlan': 'Segmento de VLAN',
            'barra_vlan': 'Barra de VLAN',
            'uso_red': 'Uso de Red',
            'cloud': 'Cloud',
            'ambiente': 'Ambiente',
            'proyecto': 'Proyecto'
        }
        widgets = {
            'numero_vlan': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese el número de VLAN (1-4094)'
            }),
            'segmento_vlan': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ejemplo: 172.22.190.0'
            }),
            'barra_vlan': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ingrese la máscara (0-32)'
            }),
            'uso_red': forms.Select(attrs={
                'class': 'form-control'
            }),
            'cloud': forms.Select(attrs={
                'class': 'form-control'
            }),
            'ambiente': forms.Select(attrs={
                'class': 'form-control'
            }),
            'proyecto': forms.Select(attrs={
                'class': 'form-control',
                'style': 'display: none;'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['proyecto'].required = False
        self.fields['ambiente'].required = True
        
        # Agregar clases de Bootstrap a todos los campos
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control'

class ProyectoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Obtener el perfil de Arquitecto
        perfil_arquitecto = Perfil.objects.filter(nombre_perfil='Arquitecto').first()
        if perfil_arquitecto:
            # Filtrar usuarios con perfil de Arquitecto
            arquitectos = User.objects.filter(usuarioextendido__perfiles=perfil_arquitecto)
            self.fields['arquitecto'].queryset = arquitectos

    class Meta:
        model = PROYECTO
        fields = ['nombre_proyecto', 'fecha_solicitud', 'fecha_asignacion', 'solicitante', 'arquitecto', 'uso_red']
        widgets = {
            'fecha_solicitud': forms.DateInput(attrs={'type': 'date'}),
            'fecha_asignacion': forms.DateInput(attrs={'type': 'date'}),
            'solicitante': forms.Select(attrs={'class': 'form-control'}),
            'arquitecto': forms.Select(attrs={'class': 'form-control'}),
            'uso_red': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre_proyecto': 'Nombre del Proyecto',
            'fecha_solicitud': 'Fecha de Solicitud',
            'fecha_asignacion': 'Fecha de Asignación',
            'solicitante': 'Solicitante',
            'arquitecto': 'Arquitecto',
            'uso_red': 'Uso de Red',
        }

class StatusProyectoForm(forms.ModelForm):
    class Meta:
        model = STATUS_PROYECTO
        fields = ['nombre_status', 'descripcion_status']
        widgets = {
            'nombre_status': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del estado'}),
            'descripcion_status': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción del estado', 'rows': 3}),
        }
        labels = {
            'nombre_status': 'Nombre del Estado',
            'descripcion_status': 'Descripción',
        }

class PaisForm(forms.ModelForm):
    class Meta:
        model = PAIS
        fields = ['nombre_pais', 'abreviatura_pais']
        labels = {
            'nombre_pais': 'Nombre del País',
            'abreviatura_pais': 'Abreviatura'
        }
        widgets = {
            'nombre_pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del país'}),
            'abreviatura_pais': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese la abreviatura (ej: ESP, USA)'}),
        }

class RedForm(forms.ModelForm):
    class Meta:
        model = RED
        fields = ['nombre_red', 'descripcion_red']
        labels = {
            'nombre_red': 'Nombre de la Red',
            'descripcion_red': 'Descripción'
        }
        widgets = {
            'nombre_red': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre de la red'}),
            'descripcion_red': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción de la red', 'rows': 3}),
        }

class UsoRedForm(forms.ModelForm):
    class Meta:
        model = USO_RED
        fields = ['nombre_uso', 'descripcion_uso']
        labels = {
            'nombre_uso': 'Nombre del Uso',
            'descripcion_uso': 'Descripción'
        }
        widgets = {
            'nombre_uso': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ingrese el nombre del uso'}),
            'descripcion_uso': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Ingrese la descripción del uso', 'rows': 3}),
        }
