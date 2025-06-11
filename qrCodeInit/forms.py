from django import forms

class GeradorQrCodeZipForm(forms.Form):
    codigo_base = forms.CharField(
        label='Código Base',
        max_length=100,
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

class GerarAdesivoArboForm(forms.Form):
    codigo_inicial = forms.CharField(
        label='Código Inicial',
        max_length=100,
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'Ex: ARBO-001'}
        ),
    )
    quantidade = forms.IntegerField(
        label='Quantidade de Adesivos',
        min_value=1,
        widget=forms.NumberInput(
            attrs={'class': 'form-control', 'placeholder': 'Ex: 10'}
        ),
    )
    cidade_logo = forms.ImageField(
        label='Logo da Cidade (enviada pelo usuário)',
        allow_empty_file=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'}),
    )