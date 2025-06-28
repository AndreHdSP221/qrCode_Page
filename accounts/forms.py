from django import forms
from django.contrib.auth.forms import UserCreationForm 
from .models import CustomUser

class Verify2FACodeForm(forms.Form):
    code = forms.CharField(label="Código de Verificação", max_length=6, required=True)

class CreateNewAccountForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['fullname'].widget.attrs.update({
            'type': 'text',
            'id': 'fullname',
            'placeholder': 'Digite seu nome completo',
            'required': True,
        })

        self.fields['username'].widget.attrs.update({
            'type': 'username',
            'id': 'username',
            'name': 'username',
            'placeholder': 'Como aparecerá no site',
            'required': True
        })

        self.fields['email'].widget.attrs.update({
            'type': 'email',
            'id': 'email',
            'name': 'email',
            'placeholder': 'seu.email@exemplo.com',
            'required': True
        })

        self.fields['password1'].widget.attrs.update({
            'placeholder': 'Crie uma senha forte',
            'id': 'password',
        })
        
        self.fields['password2'].widget.attrs.update({
            'placeholder': 'Confirme sua senha',
            'id': 'password2',
        })

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ['username', 'fullname', 'email']
