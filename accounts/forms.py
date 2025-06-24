from django import forms

class Verify2FACodeForm(forms.Form):
    code = forms.CharField(label="Código de Verificação", max_length=6, required=True)
    