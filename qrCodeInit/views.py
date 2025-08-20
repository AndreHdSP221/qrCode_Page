import io
import zipfile

import qrcode
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .forms import GeradorQrCodeZipForm

@login_required
def gerar_zip_qrcodes(request: HttpRequest) -> HttpResponse:
    template_name = 'qrcodetpl/pages/qrCodeSequencial.html'
    form = GeradorQrCodeZipForm()

    if request.method == 'POST':
        form = GeradorQrCodeZipForm(request.POST)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            codigo_base = cleaned_data['codigo_base']
            quantidadeInicial = cleaned_data['quantidadeInicial']
            quantidadeFinal = cleaned_data['quantidadeFinal']

            try:
                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:

                    for i in range(quantidadeInicial, quantidadeFinal + 1):
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
                messages.error(request, f"Ocorreu um erro inesperado ao gerar o arquivo: {e}")
        else:
            messages.error(request, 'Dados inválidos. Por favor, verifique os campos.')

    return render(request, template_name, {'form': form})
