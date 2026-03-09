from django.db import models


class Medicamento(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(verbose_name="Descripción")
    dosis = models.CharField(max_length=100, verbose_name="Dosis")

    class Meta:
        verbose_name = "Medicamento"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Cliente(models.Model):
    cedula = models.CharField(max_length=20, unique=True, verbose_name="Cédula")
    nombres = models.CharField(max_length=100, verbose_name="Nombres")
    apellidos = models.CharField(max_length=100, verbose_name="Apellidos")
    direccion = models.CharField(max_length=200, verbose_name="Dirección")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono")

    class Meta:
        verbose_name = "Cliente"
        ordering = ['apellidos', 'nombres']

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


class Mascota(models.Model):
    identificacion = models.CharField(max_length=20, unique=True, verbose_name="Identificación")
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    raza = models.CharField(max_length=100, verbose_name="Raza")
    edad = models.PositiveIntegerField(verbose_name="Edad (años)")
    peso = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Peso (kg)")
    medicamento = models.ForeignKey(
        Medicamento, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name="Medicamento", related_name="mascotas"
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.CASCADE,
        verbose_name="Cliente", related_name="mascotas"
    )

    class Meta:
        verbose_name = "Mascota"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.identificacion})"