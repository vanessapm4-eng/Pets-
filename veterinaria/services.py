from django.db.models import Q, Count
from .models import Mascota, Cliente, Medicamento


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