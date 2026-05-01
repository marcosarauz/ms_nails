from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth import login
from .models import Servicio, Cliente, Turno, HorarioTrabajo, DiaBloqueado
from .forms import ServicioForm  # <--- Paso 1: Importamos el formulario
from urllib.parse import quote
from datetime import date, datetime, timedelta


def es_duena(user):
    return user.is_authenticated and user.is_staff


def generar_horarios(hora_inicio, hora_fin, intervalo_minutos=30):
    horarios = []
    inicio = datetime.combine(date.today(), hora_inicio)
    fin = datetime.combine(date.today(), hora_fin)

    actual = inicio
    while actual < fin:
        horarios.append(actual.time().strftime("%H:%M"))
        actual += timedelta(minutes=intervalo_minutos)

    return horarios


def hay_superposicion(fecha, hora, servicio):
    inicio_nuevo = datetime.combine(
        fecha,
        datetime.strptime(hora, "%H:%M").time()
    )
    fin_nuevo = inicio_nuevo + timedelta(minutes=servicio.duracion)

    turnos_del_dia = Turno.objects.filter(fecha=fecha).exclude(estado='cancelado')

    for turno in turnos_del_dia:
        inicio_existente = datetime.combine(fecha, turno.hora)
        fin_existente = inicio_existente + timedelta(minutes=turno.servicio.duracion)

        if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
            return True

    return False


def reservar_turno(request):
    # Si no está logueado, ve portada pública
    if not request.user.is_authenticated:
        return render(request, 'home.html')

    # Si es dueña/staff, entra al panel
    if request.user.is_staff:
        return redirect('dashboard')

    servicios = Servicio.objects.all()
    fecha_seleccionada = request.GET.get('fecha')
    servicio_seleccionado = request.GET.get('servicio')

    horarios_disponibles = []
    error = None
    servicio_actual = None

    if servicio_seleccionado:
        try:
            servicio_actual = Servicio.objects.get(id=servicio_seleccionado)
        except Servicio.DoesNotExist:
            servicio_actual = None

    if fecha_seleccionada and servicio_actual:
        fecha_obj = datetime.strptime(fecha_seleccionada, "%Y-%m-%d").date()
        dia_bloqueado = DiaBloqueado.objects.filter(fecha=fecha_obj).first()

        if dia_bloqueado:
            error = f"No hay turnos disponibles para ese día. Motivo: {dia_bloqueado.motivo}"
        else:
            dia_semana = fecha_obj.weekday()

            horarios_trabajo = HorarioTrabajo.objects.filter(
                dia=dia_semana,
                activo=True
            )

            for horario_trabajo in horarios_trabajo:
                horarios_base = generar_horarios(
                    horario_trabajo.hora_inicio,
                    horario_trabajo.hora_fin,
                    intervalo_minutos=30
                )

                for horario in horarios_base:
                    inicio = datetime.combine(
                        fecha_obj,
                        datetime.strptime(horario, "%H:%M").time()
                    )
                    fin = inicio + timedelta(minutes=servicio_actual.duracion)
                    fin_jornada = datetime.combine(fecha_obj, horario_trabajo.hora_fin)

                    if fin <= fin_jornada:
                        ocupado = hay_superposicion(
                            fecha_obj,
                            horario,
                            servicio_actual
                        )

                        if not ocupado:
                            horarios_disponibles.append(horario)

    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

        servicio = Servicio.objects.get(id=servicio_id)
        fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()

        cliente, _ = Cliente.objects.get_or_create(
            usuario=request.user,
            defaults={
                'nombre': nombre,
                'telefono': telefono
            }
        )

        cliente.nombre = nombre
        cliente.telefono = telefono
        cliente.save()

        if hay_superposicion(fecha_obj, hora, servicio):
            return render(request, 'reservar.html', {
                'servicios': servicios,
                'horarios': horarios_disponibles,
                'fecha_seleccionada': fecha,
                'servicio_seleccionado': servicio_id,
                'error': 'Ese horario ya está ocupado o se superpone con otro turno'
            })

        Turno.objects.create(
            cliente=cliente,
            servicio=servicio,
            fecha=fecha,
            hora=hora
        )

        mensaje = (
            f"Hola! Quiero confirmar turno:\n\n"
            f"Nombre: {nombre}\n"
            f"Servicio: {servicio.nombre}\n"
            f"Fecha: {fecha}\n"
            f"Hora: {hora}"
        )
        mensaje_url = quote(mensaje)

        # Cambiar por el número real de la dueña
        numero = "5491123456789"

        return redirect(f"https://wa.me/{numero}?text={mensaje_url}")

    return render(request, 'reservar.html', {
        'servicios': servicios,
        'horarios': horarios_disponibles,
        'fecha_seleccionada': fecha_seleccionada,
        'servicio_seleccionado': servicio_seleccionado,
        'error': error
    })


def registro(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        telefono = request.POST.get('telefono')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            return render(request, 'registro.html', {
                'error': 'Ese usuario ya existe'
            })

        usuario = User.objects.create_user(
            username=username,
            password=password,
            first_name=nombre
        )

        Cliente.objects.create(
            usuario=usuario,
            nombre=nombre,
            telefono=telefono
        )

        login(request, usuario)
        return redirect('reservar')

    return render(request, 'registro.html')


@login_required
def mis_turnos(request):
    if request.user.is_staff:
        return redirect('dashboard')

    cliente = Cliente.objects.filter(usuario=request.user).first()
    turnos = []

    if cliente:
        turnos = Turno.objects.filter(cliente=cliente).order_by('-fecha', '-hora')

    return render(request, 'mis_turnos.html', {
        'turnos': turnos
    })


@user_passes_test(es_duena)
def dashboard(request):
    hoy = date.today()

    turnos_hoy = Turno.objects.filter(fecha=hoy).order_by('hora')
    pendientes = Turno.objects.filter(estado='pendiente').count()
    confirmados = Turno.objects.filter(estado='confirmado').count()
    finalizados = Turno.objects.filter(estado='finalizado').count()
    cancelados = Turno.objects.filter(estado='cancelado').count()

    return render(request, 'dashboard.html', {
        'turnos_hoy': turnos_hoy,
        'pendientes': pendientes,
        'confirmados': confirmados,
        'finalizados': finalizados,
        'cancelados': cancelados,
    })


@user_passes_test(es_duena)
def agenda(request):
    fecha = request.GET.get('fecha')

    if fecha:
        turnos = Turno.objects.filter(fecha=fecha).order_by('fecha', 'hora')
    else:
        turnos = Turno.objects.all().order_by('fecha', 'hora')

    return render(request, 'agenda.html', {
        'turnos': turnos,
        'fecha': fecha
    })

@user_passes_test(es_duena)
def cambiar_estado(request, id, estado):
    turno = get_object_or_404(Turno, id=id)
    turno.estado = estado
    turno.save()
    return redirect('agenda')


@user_passes_test(es_duena)
def configuracion(request):
    return render(request, 'configuracion.html')


@user_passes_test(es_duena)
def gestion_servicios(request):
    """Vista estética para que la dueña maneje los servicios"""
    servicios = Servicio.objects.all()
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_servicios')
    else:
        form = ServicioForm()
    
    return render(request, 'gestion_servicios.html', {
        'servicios': servicios,
        'form': form
    })


def gracias(request):
    return render(request, 'gracias.html')