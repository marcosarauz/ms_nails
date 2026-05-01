from django.contrib import admin
from .models import Servicio, Cliente, Turno, HorarioTrabajo, DiaBloqueado

admin.site.site_header = "MstodaBella Nails"
admin.site.site_title = "Panel MstodaBella"
admin.site.index_title = "Gestión del negocio"


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'duracion', 'precio')
    search_fields = ('nombre',)
    list_per_page = 20


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'telefono', 'usuario')
    search_fields = ('nombre', 'telefono', 'usuario__username')
    list_per_page = 20


@admin.register(Turno)
class TurnoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'hora', 'cliente', 'telefono_cliente', 'servicio', 'estado')
    list_filter = ('estado', 'fecha', 'servicio')
    search_fields = ('cliente__nombre', 'cliente__telefono', 'servicio__nombre')
    ordering = ('-fecha', 'hora')
    list_editable = ('estado',)
    date_hierarchy = 'fecha'
    list_per_page = 25

    def telefono_cliente(self, obj):
        return obj.cliente.telefono

    telefono_cliente.short_description = "Teléfono"


@admin.register(HorarioTrabajo)
class HorarioTrabajoAdmin(admin.ModelAdmin):
    list_display = ('dia', 'hora_inicio', 'hora_fin', 'activo')
    list_filter = ('dia', 'activo')
    list_editable = ('hora_inicio', 'hora_fin', 'activo')


@admin.register(DiaBloqueado)
class DiaBloqueadoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'motivo')
    search_fields = ('motivo',)
    date_hierarchy = 'fecha'