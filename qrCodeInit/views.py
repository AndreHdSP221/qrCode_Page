import io
import re
import zipfile

import qrcode
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

from .forms import GeradorQrCodeZipForm, GerarAdesivoArboForm


def extrair_prefixo_e_numero(codigo):
    match = re.match(r'^(.*?)(\d+)$', codigo)
    if not match:
        raise ValueError(
            "O formato do código inicial é inválido. Deve terminar com números."
        )

    prefixo, numero_str = match.groups()
    numero = int(numero_str)
    padding = len(numero_str)

    return prefixo, numero, padding


def gerar_adesivos_arbo(request):
    if request.method == 'POST':
        form = GerarAdesivoArboForm(request.POST, request.FILES)
        if form.is_valid():
            codigo_inicial = form.cleaned_data['codigo_inicial']
            quantidade = form.cleaned_data['quantidade']
            cidade_logo_file = form.cleaned_data['cidade_logo']

            try:
                prefixo, numero_inicial, padding = extrair_prefixo_e_numero(
                    codigo_inicial
                )
            except ValueError as e:
                return render(
                    request,
                    'qrcodetpl/pages/pageadesivoarbo.html',
                    {'form': form, 'error': str(e)},
                )

            imagens_adesivos_buffers = []

            for i in range(quantidade):
                codigo_atual = f"{prefixo}{str(numero_inicial + i).zfill(padding)}"
                qr_img = qrcode.make(codigo_atual, box_size=10, border=2).convert('RGB')
                logo_cidade = Image.open(cidade_logo_file).convert("RGBA")

                qr_img = qr_img.resize((250, 250))
                logo_cidade = logo_cidade.resize((100, 100))

                draw = ImageDraw.Draw(logo_cidade)
                try:
                    font = ImageFont.truetype("arial.ttf", 24)
                except IOError:
                    font = ImageFont.load_default()
                draw.text((50, 320), codigo_atual, font=font, fill="black")

                buffer = io.BytesIO()
                logo_cidade.save(buffer, format='PNG')
                buffer.seek(0)
                imagens_adesivos_buffers.append(buffer)
                
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = (
                'attachment; filename="adesivos_arbo.pdf"'
            )

            pdf_canvas = canvas.Canvas(response, pagesize=letter)
            width, height = letter
            x_offset, y_offset, margin = 50, height - 220, 20
            adesivo_width, adesivo_height = 250, 180
            adesivos_por_pagina = 8

            for idx, img_buffer in enumerate(imagens_adesivos_buffers):
                if idx > 0 and idx % adesivos_por_pagina == 0:
                    pdf_canvas.showPage() 
                    y_offset = height - 220 

                col = idx % 2
                row = (idx // 2) % 4
                x = x_offset + col * (adesivo_width + margin)
                y = y_offset - row * (adesivo_height + margin)

                pdf_canvas.drawImage(
                    ImageReader(img_buffer),
                    x,
                    y,
                    width=adesivo_width,
                    height=adesivo_height,
                )

            pdf_canvas.save()
            return response
    else:
        form = GerarAdesivoArboForm()

    return render(
        request, 'qrcodetpl/pages/pageadesivoarbo.html', {'form': form}
    )


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


def qr_code_view(request):
    return render(request, 'qrcodetpl/pages/qrCodeSequencial.html')