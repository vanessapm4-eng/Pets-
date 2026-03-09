from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from .models import Mascota, Cliente, Medicamento
from .forms import MascotaForm, ClienteForm, MedicamentoForm
from .services import MascotaService, ClienteService, MedicamentoService


# DASHBOARD
def dashboard(request):
    context = {
        'total_mascotas': Mascota.objects.count(),
        'total_clientes': Cliente.objects.count(),
        'total_medicamentos': Medicamento.objects.count(),
    }
    return render(request, 'veterinaria/dashboard.html', context)


# MASCOTAS
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

def mascota_eliminar(request, pk):
    mascota = get_object_or_404(Mascota, pk=pk)
    if request.method == 'POST':
        mascota.delete()
        messages.success(request, 'Mascota eliminada.')
        return redirect('mascota_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': mascota})


# CLIENTES
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

def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        cliente.delete()
        messages.success(request, 'Cliente eliminado.')
        return redirect('cliente_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': cliente})


# MEDICAMENTOS
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

def medicamento_eliminar(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)
    if request.method == 'POST':
        medicamento.delete()
        messages.success(request, 'Medicamento eliminado.')
        return redirect('medicamento_lista')
    return render(request, 'veterinaria/confirmar_eliminar.html', {'objeto': medicamento})


# REPORTES
def reporte_medicamentos(request):
    medicamentos = MedicamentoService.reporte()
    return render(request, 'veterinaria/reporte_medicamentos.html', {'medicamentos': medicamentos})

def reporte_clientes(request):
    clientes = ClienteService.reporte()
    return render(request, 'veterinaria/reporte_clientes.html', {'clientes': clientes})