from django.contrib import admin
from .models import AMBIENTE

class AmbienteAdmin(admin.ModelAdmin):
    readonly_fields = ("fecha_creacion",)

# Register your models here.
admin.site.register(AMBIENTE, AmbienteAdmin)