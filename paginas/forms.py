from django import forms


class ConsultaContactoForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "name",
                "placeholder": "Tu nombre",
            }
        ),
    )
    correo = forms.EmailField(
        label="Correo",
        max_length=254,
        widget=forms.EmailInput(
            attrs={
                "class": "form-control",
                "autocomplete": "email",
                "placeholder": "tucorreo@ejemplo.cl",
            }
        ),
    )
    telefono = forms.CharField(
        label="Teléfono",
        max_length=30,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "autocomplete": "tel",
                "placeholder": "+56 9 ...",
            }
        ),
    )
    mensaje = forms.CharField(
        label="Mensaje",
        max_length=3000,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 5,
                "placeholder": "Cuéntanos qué maquinaria buscas...",
            }
        ),
    )
