from django import forms

class GeradorAdesivosForm(forms.Form):

    logo = forms.ImageField(
        label="Logo da Empresa",
        help_text="Envie um arquivo de imagem (PNG, JPG, etc.)",
        required=True
    )
    codigo_base = forms.CharField(
        label="Código Base",
        max_length=100,
        required=True,
        help_text="Ex: PROD-ABC"
    )
    quantidade = forms.IntegerField(
        label="Quantidade de Adesivos",
        min_value=1,
        max_value=5000,
        required=True,
        help_text="O número de adesivos a serem gerados."
    )

class GeradorQrCodeZipForm(forms.Form):

    codigo_base = forms.CharField(
        label="Código Base",
        max_length=100,
        required=True,
        help_text="Ex: LOTE-XYZ"
    )
    quantidade = forms.IntegerField(
        label="Quantidade de QR Codes",
        min_value=1,
        max_value=10000, # Limite de segurança
        required=True,
        help_text="O número de QR Codes a serem gerados."
    )