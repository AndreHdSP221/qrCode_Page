import io
import re
import os
import zipfile
import qrcode
from PIL import Image, ImageDraw, ImageFont

from django.shortcuts import render
from django.http import HttpResponse, HttpRequest
from django.conf import settings
from django.contrib import messages

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

from .forms import GerarAdesivoArboForm, GeradorQrCodeZipForm

def extrair_prefixo_e_numero(codigo):
    match = re.match(r'^(.*?)(\d+)$', codigo)
    if not match:
        raise ValueError("O formato do código inicial é inválido. Deve terminar com números.")
    prefixo, numero_str = match.groups()
    return prefixo, int(numero_str), len(numero_str)

def gerar_adesivos_arbo(request):
    if request.method == 'POST':
        form = GerarAdesivoArboForm(request.POST, request.FILES)
        if form.is_valid():
            codigo_inicial = form.cleaned_data['codigo_inicial']
            quantidade = form.cleaned_data['quantidade']
            cidade_logo_file = form.cleaned_data['cidade_logo']

            try:
                prefixo, numero_inicial, padding = extrair_prefixo_e_numero(codigo_inicial)
            except ValueError as e:
                messages.error(request, str(e))
                return render(request, 'qrcodetpl/pages/pageadesivoarbo.html', {'form': form})

            try:
                path_base_image = os.path.join(settings.BASE_DIR, 'qrcode/images/Sticker_Dominus.png')
                path_font_code = os.path.join(settings.BASE_DIR, 'qrcode/fonts/Myriadpro/MYRIADPRO-BOLDCOND.OTF')
                
                imagem_base_original = Image.open(path_base_image).convert("RGBA")
                font_code = ImageFont.truetype(path_font_code, 26)
            except FileNotFoundError as e:
                messages.error(request, f"Erro crítico: Arquivo estático não encontrado: {e.filename}")
                return render(request, 'qrcodetpl/pages/pageadesivoarbo.html', {'form': form})

            try:
                logo_cidade = Image.open(cidade_logo_file).convert("RGBA")
            except Exception as e:
                messages.error(request, f"Erro ao processar a imagem da cidade: {e}")
                return render(request, 'qrcodetpl/pages/pageadesivoarbo.html', {'form': form})

            imagens_adesivos_buffers = []

            for i in range(quantidade):
                adesivo_atual = imagem_base_original.copy()
                codigo_atual = f"{prefixo}{str(numero_inicial + i).zfill(padding)}"
                qr_img = qrcode.make(codigo_atual, border=1).convert("RGBA").resize((280, 280))

                logo_cidade_resized = logo_cidade.resize((450, 110))
                adesivo_atual.paste(logo_cidade_resized, (380, 45), logo_cidade_resized)
                adesivo_atual.paste(qr_img, (50, 180), qr_img)

                draw = ImageDraw.Draw(adesivo_atual)
                draw.text((65, 420), codigo_atual, font=font_code, fill="white")

                buffer = io.BytesIO()
                adesivo_atual.save(buffer, format='PNG')
                buffer.seek(0)
                imagens_adesivos_buffers.append(buffer)
                
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="adesivos_arbo.pdf"'

            pdf_canvas = canvas.Canvas(response, pagesize=letter)
            width, height = letter
            x_offset, y_offset, margin = 40, height - 120, 15
            adesivo_width, adesivo_height = 250, 125 
            adesivos_por_pagina = 8

            for idx, img_buffer in enumerate(imagens_adesivos_buffers):
                if idx > 0 and idx % adesivos_por_pagina == 0:
                    pdf_canvas.showPage() 
                    y_offset = height - 120

                col = idx % 2
                row = (idx // 2) % 4
                x = x_offset + col * (adesivo_width + margin)
                y = y_offset - row * (adesivo_height + margin)

                pdf_canvas.drawImage(ImageReader(img_buffer), x, y, width=adesivo_width, height=adesivo_height, mask='auto')

            pdf_canvas.save()
            return response
    else:
        form = GerarAdesivoArboForm()

    return render(request, 'qrcodetpl/pages/pageadesivoarbo.html', {'form': form})


def gerar_zip_qrcodes(request: HttpRequest) -> HttpResponse:
    template_name = 'qrcodetpl/pages/qrCodeSequencial.html'

    if request.method != 'POST':
        form = GeradorQrCodeZipForm()
        return render(request, template_name, {'form': form})

    form = GeradorQrCodeZipForm(request.POST)
    if not form.is_valid():
        messages.error(request, 'Dados inválidos. Por favor, verifique os campos.')
        return render(request, template_name, {'form': form})

    codigo_base = form.cleaned_data['codigo_base'].strip().replace(" ", "_").upper()
    quantidade = form.cleaned_data['quantidade']

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
        response['Content-Disposition'] = f'attachment; filename="qrcodes_{codigo_base}.zip"'
        return response

    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado: {e}")
        return render(request, template_name, {'form': form})


def qr_code_view(request):
    return render(request, 'qrcodetpl/pages/qrCodeSequencial.html')
