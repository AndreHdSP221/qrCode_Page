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
from django.contrib.staticfiles import finders

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
                prefixo, numero_inicial, padding = extrair_prefixo_e_numero(codigo_inicial)
            except ValueError as e:
                return render(
                    request,
                    'qrcodetpl/pages/pageadesivoarbo.html',
                    {'form': form, 'error': str(e)},
                )

            # --- Lógica de Geração de Imagem Adaptada ---
            caminho_base_sticker = finders.find('images/Sticker_Dominus.png')
            caminho_da_fonte = finders.find('fonts/MYRIADPRO-BOLDCOND.OTF')

            if not caminho_base_sticker or not caminho_da_fonte:
                error_msg = "Erro: Arquivo de base do adesivo ou fonte não encontrado nos arquivos estáticos."
                return render(
                    request,
                    'qrcodetpl/pages/pageadesivoarbo.html',
                    {'form': form, 'error': error_msg},
                )
            
            imagens_adesivos_buffers = []
            logo_cidade_pil = Image.open(cidade_logo_file).convert("RGBA")

            for i in range(quantidade):
                # Carrega a imagem de base para cada adesivo para não modificar a original
                imagem_base = Image.open(caminho_base_sticker).convert("RGBA")
                
                # 1. Gera o código e o QR Code
                codigo_atual = f"{prefixo}{str(numero_inicial + i).zfill(padding)}"
                qr_img_pil = qrcode.make(codigo_atual, box_size=10, border=2).convert('RGBA')

                # 2. Cola o QR Code na imagem base (lógica de pastqrCode)
                qr_largura, qr_altura = qr_img_pil.size
                novo_tamanho_qr = (round(qr_largura * 1.3), round(qr_altura * 1.3))
                qr_img_redimensionada = qr_img_pil.resize(novo_tamanho_qr, resample=Image.Resampling.BICUBIC)
                posicao_qr = (-5, 138)
                imagem_base.paste(qr_img_redimensionada, posicao_qr, qr_img_redimensionada)

                # 3. Cola o logo da cidade na imagem base (lógica de pastLogoCity)
                marge_x_logo = 35
                marge_y_logo = 400
                posicao_x_logo = imagem_base.width - logo_cidade_pil.width - marge_x_logo
                posicao_y_logo = imagem_base.height - logo_cidade_pil.height - marge_y_logo
                posicao_logo = (posicao_x_logo, posicao_y_logo)
                imagem_base.paste(logo_cidade_pil, posicao_logo, logo_cidade_pil)

                # 4. Escreve o texto na imagem base (lógica de drawTextInImage)
                draw = ImageDraw.Draw(imagem_base)
                try:
                    font_size = 36
                    fonte = ImageFont.truetype(caminho_da_fonte, size=font_size)
                except IOError:
                    fonte = ImageFont.load_default()
                
                text_bbox = draw.textbbox((0, 0), codigo_atual, font=fonte)
                text_width = text_bbox[2] - text_bbox[0]
                text_height = text_bbox[3] - text_bbox[1]
                
                marge_x_texto = 569
                marge_y_texto = 98
                posicao_x_texto = imagem_base.width - text_width - marge_x_texto
                posicao_y_texto = imagem_base.height - text_height - marge_y_texto
                posicao_texto = (posicao_x_texto, posicao_y_texto)

                draw.text(posicao_texto, codigo_atual, font=fonte, fill="white")

                # Salva a imagem finalizada no buffer
                buffer = io.BytesIO()
                imagem_base.save(buffer, format='PNG')
                buffer.seek(0)
                imagens_adesivos_buffers.append(buffer)

            # --- Lógica de Geração de PDF (inalterada) ---
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="adesivos_arbo.pdf"'
            
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