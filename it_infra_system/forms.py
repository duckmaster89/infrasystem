from django.forms import ModelForm
from .models import AMBIENTE, SOLICITANTE, GERENCIA, PUESTO
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
