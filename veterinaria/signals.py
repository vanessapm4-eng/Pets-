from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db.models.signals import post_migrate
from django.dispatch import receiver

User = get_user_model()

ROLES_SISTEMA = ['Admin', 'Recepcionista', 'Veterinario']


@receiver(post_migrate)
def crear_roles_y_admin_por_defecto(sender, **kwargs):
    if sender.name != 'veterinaria':
        return

    for rol in ROLES_SISTEMA:
        Group.objects.get_or_create(name=rol)

    admin_group = Group.objects.get(name='Admin')

    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'is_active': True,
        }
    )

    if created:
        admin_user.set_password('admin')
        admin_user.save()

    admin_user.groups.add(admin_group)

    PerfilUsuario = apps.get_model('veterinaria', 'PerfilUsuario')
    PerfilUsuario.objects.get_or_create(
        user=admin_user,
        defaults={
            'nombres': 'Administrador',
            'apellidos': 'Principal',
            'telefono': '',
            'documento': '',
        }
    )