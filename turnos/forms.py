from django import forms
from .models import Servicio, Turno

# Formulario para la gestión de Servicios
class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'duracion', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
        }

# Formulario para la gestión de Turnos (El nuevo que agregamos)
class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['cliente', 'servicio', 'fecha', 'hora', 'estado']
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select rounded-pill border-rosa'}),
            'servicio': forms.Select(attrs={'class': 'form-select rounded-pill border-rosa'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control rounded-pill border-rosa', 'type': 'date'}),
            'hora': forms.TimeInput(attrs={'class': 'form-control rounded-pill border-rosa', 'type': 'time'}),
            'estado': forms.Select(attrs={'class': 'form-select rounded-pill border-rosa'}),
        }