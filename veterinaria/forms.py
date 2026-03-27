from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password

from .models import Mascota, Cliente, Medicamento

User = get_user_model()

ROLES_SISTEMA = ['Admin', 'Recepcionista', 'Veterinario']


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Usuario',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña',
            'autocomplete': 'current-password'
        })
    )


class UsuarioCreacionForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documento = forms.CharField(
        label="Documento",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text="Mínimo 8 caracteres, 1 mayúscula, 1 número y 1 carácter especial."
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    roles = forms.ModelMultipleChoiceField(
        label="Roles",
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    is_active = forms.BooleanField(
        label="Usuario activo",
        required=False,
        initial=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['roles'].queryset = Group.objects.filter(name__in=ROLES_SISTEMA).order_by('name')

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        username = cleaned_data.get('username')
        nombres = cleaned_data.get('nombres')
        apellidos = cleaned_data.get('apellidos')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Las contraseñas no coinciden.")

        if password1:
            temp_user = User(
                username=username,
                first_name=nombres or '',
                last_name=apellidos or ''
            )
            validate_password(password1, temp_user)

        return cleaned_data


class UsuarioEdicionForm(forms.Form):
    username = forms.CharField(
        label="Usuario",
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nombres = forms.CharField(
        label="Nombres",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    apellidos = forms.CharField(
        label="Apellidos",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    documento = forms.CharField(
        label="Documento",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password1 = forms.CharField(
        label="Nueva contraseña",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'}),
        help_text="Déjala vacía si no deseas cambiarla."
    )
    password2 = forms.CharField(
        label="Confirmar nueva contraseña",
        strip=False,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'autocomplete': 'new-password'})
    )
    roles = forms.ModelMultipleChoiceField(
        label="Roles",
        queryset=Group.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )
    is_active = forms.BooleanField(
        label="Usuario activo",
        required=False
    )

    def __init__(self, *args, user_instance=None, **kwargs):
        self.user_instance = user_instance
        super().__init__(*args, **kwargs)
        self.fields['roles'].queryset = Group.objects.filter(name__in=ROLES_SISTEMA).order_by('name')

        if self.user_instance and not self.is_bound:
            self.fields['username'].initial = self.user_instance.username
            self.fields['is_active'].initial = self.user_instance.is_active
            self.fields['roles'].initial = self.user_instance.groups.all()

            perfil = getattr(self.user_instance, 'perfil', None)
            if perfil:
                self.fields['nombres'].initial = perfil.nombres
                self.fields['apellidos'].initial = perfil.apellidos
                self.fields['telefono'].initial = perfil.telefono
                self.fields['documento'].initial = perfil.documento

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        qs = User.objects.filter(username__iexact=username)
        if self.user_instance:
            qs = qs.exclude(pk=self.user_instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ya existe un usuario con ese nombre.")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        username = cleaned_data.get('username')
        nombres = cleaned_data.get('nombres')
        apellidos = cleaned_data.get('apellidos')

        if password1 or password2:
            if not password1:
                self.add_error('password1', "Debes escribir la nueva contraseña.")
            if not password2:
                self.add_error('password2', "Debes confirmar la nueva contraseña.")
            if password1 and password2 and password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden.")

            if password1:
                temp_user = self.user_instance or User()
                temp_user.username = username or ''
                temp_user.first_name = nombres or ''
                temp_user.last_name = apellidos or ''
                validate_password(password1, temp_user)

        return cleaned_data


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