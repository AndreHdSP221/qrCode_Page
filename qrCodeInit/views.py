import qrcode
from django.shortcuts import render
import io
import zipfile
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


"""
Cria o qr code

Vou estudar formas de deixar isso mais rapido para
grandes quantidades de qr codes
"""
@csrf_exempt
def gerar_zip_qrcodes(request):
    if request.method == 'POST':
        codigo_base = request.POST.get('codigo')
        quantidade = int(request.POST.get('quantidade'))

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for i in range(1, quantidade + 1):
                codigo_completo = f"{codigo_base}-{str(i).zfill(4)}"
                qr = qrcode.make(codigo_completo)

                img_io = io.BytesIO()
                qr.save(img_io, format='PNG')
                img_io.seek(0)

                nome_arquivo = f"{codigo_completo}.png"
                zip_file.writestr(nome_arquivo, img_io.read())

        zip_buffer.seek(0)

        # Responsavel por enviar o arquivo .zip pro user
        response = HttpResponse(zip_buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{codigo_base}_qrcodes.zip"'
        return response

    return render(request, 'qrcodetpl/pages/home.html')
