import io
import zipfile

import qrcode
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required


from .forms import GeradorQrCodeZipForm

# Responsavel por gerar os qrCodes e entregar para o user
@login_required
def gerar_zip_qrcodes(request: HttpRequest) -> HttpResponse:
    template_name = 'qrcodetpl/pages/qrCodeSequencial.html'

    if request.method != 'POST':
        form = GeradorQrCodeZipForm()
        return render(request, template_name, {'form': form})

    form = GeradorQrCodeZipForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Dados inválidos. Por favor, verifique os campos.')
        return render(request, template_name, {'form': form})

    cleaned_data = form.cleaned_data
    codigo_base = cleaned_data['codigo_base']
    quantidade = cleaned_data['quantidade']

    try:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(1, quantidade + 1):
                codigo_completo = f"{codigo_base}-{str(i).zfill(6)}"
                qr_image = qrcode.make(codigo_completo)
                img_io = io.BytesIO()
                qr_image.save(img_io, format='PNG')
                img_io.seek(0)
                zip_file.writestr(f"{codigo_completo}.png", img_io.read())

        zip_buffer.seek(0)

        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = (
            f'attachment; filename="qrcodes_{codigo_base}.zip"'
        )
        return response

    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado: {e}")
        return render(request, template_name, {'form': form})
