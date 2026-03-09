from django import forms
from .models import Mascota, Cliente, Medicamento


class MedicamentoForm(forms.ModelForm):
    class Meta:
        model = Medicamento
        fields = ['nombre', 'descripcion', 'dosis']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del medicamento'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'dosis': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 5mg cada 8 horas'}),
        }


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['cedula', 'nombres', 'apellidos', 'direccion', 'telefono']
        widgets = {
            'cedula': forms.TextInput(attrs={'class': 'form-control'}),
            'nombres': forms.TextInput(attrs={'class': 'form-control'}),
            'apellidos': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_cedula(self):
        cedula = self.cleaned_data['cedula']
        qs = Cliente.objects.filter(cedula=cedula)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe un cliente con esta cédula.")
        return cedula


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ['identificacion', 'nombre', 'raza', 'edad', 'peso', 'medicamento', 'cliente']
        widgets = {
            'identificacion': forms.TextInput(attrs={'class': 'form-control'}),
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'raza': forms.TextInput(attrs={'class': 'form-control'}),
            'edad': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'peso': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'medicamento': forms.Select(attrs={'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_identificacion(self):
        identificacion = self.cleaned_data['identificacion']
        qs = Mascota.objects.filter(identificacion=identificacion)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError("Ya existe una mascota con esta identificación.")
        return identificacion