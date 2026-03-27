from functools import wraps

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q, Count
from django.shortcuts import redirect

from .models import Mascota, Cliente, Medicamento, PerfilUsuario

User = get_user_model()

ROLES_SISTEMA = ['Admin', 'Recepcionista', 'Veterinario']

class AutenticacionService:
    MAX_INTENTOS_FALLIDOS = 3

    @staticmethod
    def obtener_o_crear_perfil(user):
        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=user,
            defaults={
                'nombres': user.username,
                'apellidos': '',
                'telefono': '',
                'documento': '',
            }
        )
        return perfil

    @staticmethod
    def registrar_intento_fallido(username):
        if not username:
            return None

        try:
            user = User.objects.get(username__iexact=username.strip())
        except User.DoesNotExist:
            return None

        perfil = AutenticacionService.obtener_o_crear_perfil(user)

        if perfil.bloqueado_por_intentos:
            return user

        perfil.intentos_fallidos_login += 1

        if perfil.intentos_fallidos_login >= AutenticacionService.MAX_INTENTOS_FALLIDOS:
            perfil.intentos_fallidos_login = AutenticacionService.MAX_INTENTOS_FALLIDOS
            perfil.bloqueado_por_intentos = True
            user.is_active = False
            user.save()

        perfil.save()
        return user

    @staticmethod
    def reiniciar_intentos(user):
        perfil = AutenticacionService.obtener_o_crear_perfil(user)
        if perfil.intentos_fallidos_login != 0 or perfil.bloqueado_por_intentos:
            perfil.intentos_fallidos_login = 0
            perfil.bloqueado_por_intentos = False
            perfil.save()

    @staticmethod
    def esta_bloqueado_por_intentos(username):
        if not username:
            return False

        try:
            user = User.objects.select_related('perfil').get(username__iexact=username.strip())
        except User.DoesNotExist:
            return False

        perfil = getattr(user, 'perfil', None)
        if not perfil:
            return False

        return perfil.bloqueado_por_intentos


def tiene_rol(user, rol):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=rol).exists()


def tiene_algun_rol(user, roles):
    if not user.is_authenticated:
        return False
    return user.groups.filter(name__in=roles).exists()


def roles_requeridos(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')

            if request.user.is_superuser or tiene_algun_rol(request.user, roles):
                return view_func(request, *args, **kwargs)

            messages.error(request, 'No tienes permisos para acceder a este módulo.')
            return redirect('acceso_denegado')
        return _wrapped_view
    return decorator


class UsuarioService:

    @staticmethod
    def listar_todos():
        return User.objects.select_related('perfil').prefetch_related('groups').order_by('username')

    @staticmethod
    def obtener_por_id(pk):
        try:
            return User.objects.select_related('perfil').prefetch_related('groups').get(pk=pk)
        except User.DoesNotExist:
            return None

    @staticmethod
    def contar_admins_activos(exclude_user_id=None):
        qs = User.objects.filter(is_active=True, groups__name='Admin').distinct()
        if exclude_user_id:
            qs = qs.exclude(pk=exclude_user_id)
        return qs.count()

    @staticmethod
    @transaction.atomic
    def crear_usuario(cleaned_data):
        user = User.objects.create_user(
            username=cleaned_data['username'],
            password=cleaned_data['password1'],
            is_active=cleaned_data.get('is_active', True),
        )

        PerfilUsuario.objects.create(
            user=user,
            nombres=cleaned_data['nombres'],
            apellidos=cleaned_data['apellidos'],
            telefono=cleaned_data.get('telefono', ''),
            documento=cleaned_data.get('documento', ''),
        )

        user.groups.set(cleaned_data['roles'])
        return user

    @staticmethod
    @transaction.atomic
    def actualizar_usuario(usuario_editar, cleaned_data, acting_user=None):
        roles_seleccionados = cleaned_data['roles']
        nombres_roles = set(roles_seleccionados.values_list('name', flat=True))
        sera_admin = 'Admin' in nombres_roles
        seguira_activo = cleaned_data.get('is_active', False)

        es_admin_del_usuario_editado = usuario_editar.groups.filter(name='Admin').exists()

        if acting_user and acting_user.pk == usuario_editar.pk:
            if not seguira_activo:
                raise ValueError("No puedes desactivar tu propio usuario.")
            if es_admin_del_usuario_editado and not sera_admin:
                raise ValueError("No puedes quitarte tu propio rol Admin.")

        es_admin_actual = usuario_editar.groups.filter(name='Admin').exists()

        if es_admin_actual and (not sera_admin or not seguira_activo):
            admins_restantes = UsuarioService.contar_admins_activos(exclude_user_id=usuario_editar.pk)
            if admins_restantes == 0:
                raise ValueError("Debe existir al menos un administrador activo en el sistema.")


        usuario_editar.username = cleaned_data['username']
        usuario_editar.is_active = seguira_activo
        usuario_editar.save()

        perfil, _ = PerfilUsuario.objects.get_or_create(
            user=usuario_editar,
            defaults={
                'nombres': cleaned_data['nombres'],
                'apellidos': cleaned_data['apellidos'],
                'telefono': cleaned_data.get('telefono', ''),
                'documento': cleaned_data.get('documento', ''),
            }
        )

        perfil.nombres = cleaned_data['nombres']
        perfil.apellidos = cleaned_data['apellidos']
        perfil.telefono = cleaned_data.get('telefono', '')
        perfil.documento = cleaned_data.get('documento', '')

        if seguira_activo:
            perfil.intentos_fallidos_login = 0
            perfil.bloqueado_por_intentos = False

        perfil.save()

        password1 = cleaned_data.get('password1')
        if password1:
            usuario_editar.set_password(password1)
            usuario_editar.save()

        usuario_editar.groups.set(roles_seleccionados)
        return usuario_editar


class MascotaService:

    @staticmethod
    def listar_todas():
        return Mascota.objects.select_related('cliente', 'medicamento').all()

    @staticmethod
    def obtener_por_id(pk):
        try:
            return Mascota.objects.select_related('cliente', 'medicamento').get(pk=pk)
        except Mascota.DoesNotExist:
            return None

    @staticmethod
    def eliminar(pk):
        mascota = MascotaService.obtener_por_id(pk)
        if mascota:
            mascota.delete()
            return True
        return False

    @staticmethod
    def buscar(termino):
        return Mascota.objects.select_related('cliente', 'medicamento').filter(
            Q(nombre__icontains=termino) |
            Q(raza__icontains=termino) |
            Q(identificacion__icontains=termino) |
            Q(cliente__nombres__icontains=termino)
        )


class ClienteService:

    @staticmethod
    def listar_todos():
        return Cliente.objects.prefetch_related('mascotas').all()

    @staticmethod
    def obtener_por_id(pk):
        try:
            return Cliente.objects.prefetch_related('mascotas').get(pk=pk)
        except Cliente.DoesNotExist:
            return None

    @staticmethod
    def eliminar(pk):
        cliente = ClienteService.obtener_por_id(pk)
        if cliente:
            cliente.delete()
            return True
        return False

    @staticmethod
    def buscar(termino):
        return Cliente.objects.filter(
            Q(nombres__icontains=termino) |
            Q(apellidos__icontains=termino) |
            Q(cedula__icontains=termino)
        )

    @staticmethod
    def reporte():
        return Cliente.objects.annotate(
            total_mascotas=Count('mascotas')
        ).prefetch_related('mascotas__medicamento').order_by('-total_mascotas')


class MedicamentoService:

    @staticmethod
    def listar_todos():
        return Medicamento.objects.all()

    @staticmethod
    def obtener_por_id(pk):
        try:
            return Medicamento.objects.get(pk=pk)
        except Medicamento.DoesNotExist:
            return None

    @staticmethod
    def eliminar(pk):
        med = MedicamentoService.obtener_por_id(pk)
        if med:
            med.delete()
            return True
        return False

    @staticmethod
    def buscar(termino):
        return Medicamento.objects.filter(
            Q(nombre__icontains=termino) |
            Q(descripcion__icontains=termino)
        )

    @staticmethod
    def reporte():
        return Medicamento.objects.annotate(
            total_mascotas=Count('mascotas')
        ).prefetch_related('mascotas__cliente').order_by('-total_mascotas')