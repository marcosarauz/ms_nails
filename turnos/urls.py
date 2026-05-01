from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import (
    reservar_turno,
    gracias,
    agenda,
    cambiar_estado,
    dashboard,
    registro,
    mis_turnos,
    configuracion,
    gestion_servicios, # <--- Agregado
)

urlpatterns = [
    path('', reservar_turno, name='reservar'),

    path('login/', LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='reservar'), name='logout'),

    path('registro/', registro, name='registro'),
    path('mis-turnos/', mis_turnos, name='mis_turnos'),

    path('dashboard/', dashboard, name='dashboard'),
    path('agenda/', agenda, name='agenda'),
    path('configuracion/', configuracion, name='configuracion'),
    
    # Nueva ruta para la gestión estética de servicios
    path('configuracion/servicios/', gestion_servicios, name='gestion_servicios'),

    path('estado/<int:id>/<str:estado>/', cambiar_estado, name='estado'),

    path('gracias/', gracias, name='gracias'),
]