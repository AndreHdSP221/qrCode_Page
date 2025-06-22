from django import forms

class GeradorQrCodeZipForm(forms.Form):
    codigo_base = forms.CharField(
        label='Código Base',
        max_length=25,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ex: EVENTO-SP'}
        ),
    )
    quantidade = forms.IntegerField(
        label='Quantidade',
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Ex: 50'}
        ),
    )
