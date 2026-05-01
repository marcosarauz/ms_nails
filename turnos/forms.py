from django import forms
from .models import Servicio

class ServicioForm(forms.ModelForm):
    class Meta:
        model = Servicio
        fields = ['nombre', 'duracion', 'precio']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control rounded-pill'}),
            'duracion': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control rounded-pill'}),
        }