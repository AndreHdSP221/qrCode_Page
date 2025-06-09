import io
import os
import zipfile

import qrcode
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError
from reportlab.pdfgen import canvas

from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .forms import GeradorAdesivosForm, GeradorQrCodeZipForm

def draw_text(imagem_base: Image.Image, texto: str):
    
    draw = ImageDraw.Draw(imagem_base)
    caminho_fonte = os.path.join(settings.BASE_DIR, 'qrCodeInit/static/qrcode/fonts/Myriadpro/MYRIADPRO-BOLDCOND.OTF')
    try:
        fonte = ImageFont.truetype(caminho_fonte, size=36)
    except IOError:
        fonte = ImageFont.load_default()
    
    text_bbox = draw.textbbox((0, 0), texto, font=fonte)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    marge_x = 569
    marge_y = 98
    posicao_x = imagem_base.width - text_width - marge_x
    posicao_y = imagem_base.height - text_height - marge_y
    
    draw.text((posicao_x, posicao_y), texto, font=fonte, fill="white")


def paste_logo(imagem_base: Image.Image, logo_img: Image.Image):

    marge_x = 35
    marge_y = 400
    posicao_x = imagem_base.width - logo_img.width - marge_x
    posicao_y = imagem_base.height - logo_img.height - marge_y
    imagem_base.paste(logo_img, (posicao_x, posicao_y), logo_img)


def paste_qrcode(imagem_base: Image.Image, qrcode_img: Image.Image):

    novo_tamanho = (round(qrcode_img.width * 1.3), round(qrcode_img.height * 1.3))
    img_redimensionada = qrcode_img.resize(novo_tamanho, resample=Image.Resampling.BICUBIC)
    posicao = (-5, 138)
    imagem_base.paste(img_redimensionada, posicao, img_redimensionada)

def gerar_adesivos_arbo(request: HttpRequest) -> HttpResponse:
    
    template_name = 'qrcodetpl/pages/pageadesivoarbo.html'
    
    if request.method != 'POST':
        form = GeradorAdesivosForm()
        return render(request, template_name, {'form': form})

    form = GeradorAdesivosForm(request.POST, request.FILES)
    if not form.is_valid():
        messages.error(request, 'Dados inválidos. Por favor, verifique os campos.')
        return render(request, template_name, {'form': form})

    cleaned_data = form.cleaned_data
    logo_file = cleaned_data['logo']
    codigo_base = cleaned_data['codigo_base']
    quantidade = cleaned_data['quantidade']

    try:
        caminho_base_img = os.path.join(settings.BASE_DIR, 'qrCodeInit/static/qrcode/images/Sticker_Dominus.png')
        
        pdf_buffer = io.BytesIO()
        
        with Image.open(caminho_base_img) as imagem_base_original, \
             Image.open(logo_file) as logo_original:

            imagem_base_rgba = imagem_base_original.convert("RGBA")
            logo_rgba = logo_original.convert("RGBA")
            
            altura_adesivo = 283
            largura_rolo = 595
            gap_vertical = 10
            altura_total_pdf = (quantidade * altura_adesivo) + ((quantidade - 1) * gap_vertical)
            
            p = canvas.Canvas(pdf_buffer, pagesize=(largura_rolo, altura_total_pdf))
            y_atual = altura_total_pdf - altura_adesivo

            for i in range(1, quantidade + 1):
                adesivo_atual = imagem_base_rgba.copy()
                codigo_atual = f"{codigo_base}-{i:06d}"
                qrcode_img = qrcode.make(codigo_atual).convert("RGBA")

                paste_logo(adesivo_atual, logo_rgba)
                paste_qrcode(adesivo_atual, qrcode_img)
                draw_text(adesivo_atual, codigo_atual)

                with io.BytesIO() as buffer_adesivo_temp:
                    adesivo_atual.save(buffer_adesivo_temp, 'PNG')
                    buffer_adesivo_temp.seek(0)
                    p.drawImage(buffer_adesivo_temp, 0, y_atual, width=largura_rolo, height=altura_adesivo, mask='auto')
                y_atual -= (altura_adesivo + gap_vertical)
            
            p.save()

        pdf_buffer.seek(0)
        
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="adesivos_{codigo_base}.pdf"'
        return response

    except FileNotFoundError:
        messages.error(request, "Arquivo de base ou fonte não encontrado.")
        return render(request, template_name, {'form': form})
    except UnidentifiedImageError:
        messages.error(request, "O arquivo de logo enviado não é uma imagem válida.")
        return render(request, template_name, {'form': form})
    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado: {e}")
        return render(request, template_name, {'form': form})


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
        response['Content-Disposition'] = f'attachment; filename="qrcodes_{codigo_base}.zip"'
        return response
    
    except Exception as e:
        messages.error(request, f"Ocorreu um erro inesperado: {e}")
        return render(request, template_name, {'form': form})