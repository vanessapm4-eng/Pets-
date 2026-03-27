from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash, get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from .forms import (
    MascotaForm,
    ClienteForm,
    MedicamentoForm,
    LoginForm,
    UsuarioCreacionForm,
    UsuarioEdicionForm,
)
from .models import Mascota, Cliente, Medicamento
from .services import (
    MascotaService,
    ClienteService,
    MedicamentoService,
    UsuarioService,
    AutenticacionService,
    roles_requeridos,
)

User = get_user_model()


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()

        if AutenticacionService.esta_bloqueado_por_intentos(username):
            messages.error(
                request,
                'Tu usuario fue bloqueado por 3 intentos fallidos. Contacta al administrador.'
            )
            form = LoginForm(request, data=request.POST)
            return render(request, 'veterinaria/login.html', {'form': form})

        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            AutenticacionService.reiniciar_intentos(user)
            messages.success(request, f'Bienvenido, {user.username}.')
            return redirect('dashboard')

        usuario_afectado = AutenticacionService.registrar_intento_fallido(username)

        if usuario_afectado and AutenticacionService.esta_bloqueado_por_intentos(username):
            messages.error(
                request,
                'Tu usuario fue bloqueado por 3 intentos fallidos. Contacta al administrador.'
            )
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()

    return render(request, 'veterinaria/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Sesión cerrada correctamente.')
    return redirect('login')


@login_required
def acceso_denegado(request):
    return render(request, 'veterinaria/acceso_denegado.html')


@login_required
def dashboard(request):
    context = {
        'total_mascotas': Mascota.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_medicamentos': Medicamento.objects.count(),
        'total_usuarios': User.objects.count(),
    }
    return render(request, 'veterinaria/dashboard.html', context)


@roles_requeridos('Admin')
def usuario_lista(request):
    usuarios = UsuarioService.listar_todos()
    objetos = []

    for u in usuarios:
        perfil = getattr(u, 'perfil', None)
        nombre = perfil.nombre_completo if perfil else u.username
        roles = ", ".join(u.groups.values_list('name', flat=True)) or 'Sin roles'

        if u.is_active:
            estado = 'Activo'
        elif perfil and perfil.bloqueado_por_intentos:
            estado = 'Bloqueado por intentos'
        else:
            estado = 'Inactivo'

        u.valores = [u.username, nombre, roles, estado]
        u.url_editar = reverse('usuario_editar', args=[u.pk])
        objetos.append(u)

    return render(request, 'veterinaria/lista.html', {
        'titulo': 'Usuarios',
        'columnas': ['Usuario', 'Nombre', 'Roles', 'Estado'],
        'objetos': objetos,
        'url_crear': reverse('usuario_crear'),
    })


@roles_requeridos('Admin')
def usuario_crear(request):
    if request.method == 'POST':
        form = UsuarioCreacionForm(request.POST)
        if form.is_valid():
            UsuarioService.crear_usuario(form.cleaned_data)
            messages.success(request, 'Usuario creado correctamente.')
            return redirect('usuario_lista')
    else:
        form = UsuarioCreacionForm()

    return render(request, 'veterinaria/form.html', {
        'form': form,
        'titulo': 'Nuevo Usuario',
        'url_volver': reverse('usuario_lista')
    })


@roles_requeridos('Admin')
def usuario_editar(request, pk):
    usuario = get_object_or_404(User, pk=pk)

    if request.method == 'POST':
        form = UsuarioEdicionForm(request.POST, user_instance=usuario)
        if form.is_valid():
            try:
                password_cambiada = bool(form.cleaned_data.get('password1'))
                UsuarioService.actualizar_usuario(
                    usuario_editar=usuario,
                    cleaned_data=form.cleaned_data,
                    acting_user=request.user
                )

                if password_cambiada and request.user.pk == usuario.pk:
                    update_session_auth_hash(request, usuario)

                messages.success(request, 'Usuario actualizado correctamente.')
                return redirect('usuario_lista')
            except ValueError as exc:
                form.add_error(None, str(exc))
    else:
        form = UsuarioEdicionForm(user_instance=usuario)

    return render(request, 'veterinaria/form.html', {
        'form': form,
        'titulo': f'Editar Usuario: {usuario.username}',
        'url_volver': reverse('usuario_lista')
    })


@roles_requeridos('Admin', 'Recepcionista', 'Veterinario')
def mascota_lista(request):
    mascotas = MascotaService.listar_todas()
    objetos = []
    for m in mascotas:
        m.valores = [m.identificacion, m.nombre, m.raza, m.edad, m.peso]
        m.url_editar = reverse('mascota_editar', args=[m.pk])
        m.url_eliminar = reverse('mascota_eliminar', args=[m.pk])
        objetos.append(m)
    return render(request, 'veterinaria/lista.html', {
        'titulo': 'Mascotas',
        'columnas': ['ID', 'Nombre', 'Raza', 'Edad', 'Peso'],
        'objetos': objetos,
        'url_crear': reverse('mascota_crear'),
    })


@roles_requeridos('Admin', 'Recepcionista', 'Veterinario')
def mascota_crear(request):
    if request.method == 'POST':
        form = MascotaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota registrada exitosamente.')
            return redirect('mascota_lista')
    else:
        form = MascotaForm()
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Nueva Mascota',
        'url_volver': reverse('mascota_lista')
    })


@roles_requeridos('Admin', 'Recepcionista', 'Veterinario')
def mascota_editar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        form = MascotaForm(request.POST, instance=mascota)
        if form.is_valid():
            form.save()
            messages.success(request, 'Mascota actualizada.')
            return redirect('mascota_lista')
    else:
        form = MascotaForm(instance=mascota)
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Editar Mascota',
        'url_volver': reverse('mascota_lista')
    })


@roles_requeridos('Admin', 'Recepcionista', 'Veterinario')
def mascota_eliminar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada.')
        return redirect('mascota_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': mascota})


@roles_requeridos('Admin', 'Recepcionista')
def cliente_lista(request):
    clientes = ClienteService.listar_todos()
    objetos = []
    for c in clientes:
        c.valores = [c.cedula, c.nombres, c.apellidos, c.telefono, c.direccion]
        c.url_editar = reverse('cliente_editar', args=[c.pk])
        c.url_eliminar = reverse('cliente_eliminar', args=[c.pk])
        objetos.append(c)
    return render(request, 'veterinaria/lista.html', {
        'titulo': 'Clientes',
        'columnas': ['Cédula', 'Nombres', 'Apellidos', 'Teléfono', 'Dirección'],
        'objetos': objetos,
        'url_crear': reverse('cliente_crear'),
    })


@roles_requeridos('Admin', 'Recepcionista')
def cliente_crear(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente registrado exitosamente.')
            return redirect('cliente_lista')
    else:
        form = ClienteForm()
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Nuevo Cliente',
        'url_volver': reverse('cliente_lista')
    })


@roles_requeridos('Admin', 'Recepcionista')
def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado.')
            return redirect('cliente_lista')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Editar Cliente',
        'url_volver': reverse('cliente_lista')
    })


@roles_requeridos('Admin', 'Recepcionista')
def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado.')
        return redirect('cliente_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': cliente})


@roles_requeridos('Admin', 'Veterinario')
def medicamento_lista(request):
    medicamentos = MedicamentoService.listar_todos()
    objetos = []
    for m in medicamentos:
        m.valores = [m.nombre, m.descripcion, m.dosis]
        m.url_editar = reverse('medicamento_editar', args=[m.pk])
        m.url_eliminar = reverse('medicamento_eliminar', args=[m.pk])
        objetos.append(m)
    return render(request, 'veterinaria/lista.html', {
        'titulo': 'Medicamentos',
        'columnas': ['Nombre', 'Descripción', 'Dosis'],
        'objetos': objetos,
        'url_crear': reverse('medicamento_crear'),
    })


@roles_requeridos('Admin', 'Veterinario')
def medicamento_crear(request):
    if request.method == 'POST':
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento registrado exitosamente.')
            return redirect('medicamento_lista')
    else:
        form = MedicamentoForm()
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Nuevo Medicamento',
        'url_volver': reverse('medicamento_lista')
    })


@roles_requeridos('Admin', 'Veterinario')
def medicamento_editar(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        form = MedicamentoForm(request.POST, instance=medicamento)
        if form.is_valid():
            form.save()
            messages.success(request, 'Medicamento actualizado.')
            return redirect('medicamento_lista')
    else:
        form = MedicamentoForm(instance=medicamento)
    return render(request, 'veterinaria/form.html', {
        'form': form, 'titulo': 'Editar Medicamento',
        'url_volver': reverse('medicamento_lista')
    })


@roles_requeridos('Admin', 'Veterinario')
def medicamento_eliminar(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado.')
        return redirect('medicamento_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': medicamento})


@roles_requeridos('Admin', 'Veterinario')
def reporte_medicamentos(request):
    medicamentos = MedicamentoService.reporte()
    return render(request, 'veterinaria/reporte_medicamentos.html', {'medicamentos': medicamentos})


@roles_requeridos('Admin', 'Recepcionista')
def reporte_clientes(request):
    clientes = ClienteService.reporte()
    return render(request, 'veterinaria/reporte_clientes.html', {'clientes': clientes})