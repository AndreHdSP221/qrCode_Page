import io
import os
import zipfile
from typing import Dict, Any, Tuple

import qrcode
from celery import shared_task, Task
from PIL import Image, ImageDraw, ImageFont

from django.conf import settings
from django.core.files.base import ContentFile

from .models import GeracaoQRCode

try:
    STATIC_DIR = os.path.join(settings.BASE_DIR, 'qrCodeInit/static/seu_app')
    STICKER_BASE_IMAGE_PATH = os.path.join(STATIC_DIR, 'images/Sticker_Dominus.png')
    FONT_PATH = os.path.join(STATIC_DIR, 'fonts/Myriadpro/MYRIADPRO-BOLDCOND.OTF')
except Exception:
    STICKER_BASE_IMAGE_PATH = None
    FONT_PATH = None

FONT_SIZE: int = 36
TEXT_FILL_COLOR: str = "white"
TEXT_MARGINS: Tuple[int, int] = (569, 98)
LOGO_MARGINS: Tuple[int, int] = (35, 400)
QRCODE_PASTE_POSITION: Tuple[int, int] = (-5, 138)
QRCODE_RESIZE_FACTOR: float = 1.3
PDF_VERTICAL_GAP: int = 10

def draw_text_on_image(imagem_base: Image.Image, texto: str) -> None:
    draw = ImageDraw.Draw(imagem_base)
    try:
        fonte = ImageFont.truetype(FONT_PATH, size=FONT_SIZE)
    except IOError:
        fonte = ImageFont.load_default()

    text_bbox = draw.textbbox((0, 0), texto, font=fonte)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    posicao_x = imagem_base.width - text_width - TEXT_MARGINS[0]
    posicao_y = imagem_base.height - text_height - TEXT_MARGINS[1]

    draw.text((posicao_x, posicao_y), texto, font=fonte, fill=TEXT_FILL_COLOR)

def paste_logo_on_image(imagem_base: Image.Image, logo_img: Image.Image) -> None:
    posicao_x = imagem_base.width - logo_img.width - LOGO_MARGINS[0]
    posicao_y = imagem_base.height - logo_img.height - LOGO_MARGINS[1]
    imagem_base.paste(logo_img, (posicao_x, posicao_y), logo_img)

def paste_qrcode_on_image(imagem_base: Image.Image, qrcode_img: Image.Image) -> None:
    novo_tamanho = (
        round(qrcode_img.width * QRCODE_RESIZE_FACTOR),
        round(qrcode_img.height * QRCODE_RESIZE_FACTOR)
    )
    img_redimensionada = qrcode_img.resize(novo_tamanho, resample=Image.Resampling.BICUBIC)
    imagem_base.paste(img_redimensionada, QRCODE_PASTE_POSITION, img_redimensionada)

@shared_task(bind=True, max_retries=3)
def criar_pdf_adesivos_async(self: Task, form_data: Dict[str, Any], logo_content: bytes, user_id: int = None) -> str:
    from reportlab.pdfgen import canvas as reportlab_canvas

    codigo_base = form_data['codigo_base']
    quantidade = form_data['quantidade']

    print(f"Iniciando tarefa de geração de PDF para {codigo_base} ({quantidade} adesivos).")

    try:
        with Image.open(STICKER_BASE_IMAGE_PATH) as imagem_base_original, \
             Image.open(io.BytesIO(logo_content)) as logo_original:

            imagem_base_rgba = imagem_base_original.convert("RGBA")
            logo_rgba = logo_original.convert("RGBA")

            altura_adesivo = imagem_base_rgba.height
            largura_rolo = imagem_base_rgba.width
            altura_total_pdf = (quantidade * altura_adesivo) + ((quantidade - 1) * PDF_VERTICAL_GAP)

            pdf_buffer = io.BytesIO()
            p = reportlab_canvas.Canvas(pdf_buffer, pagesize=(largura_rolo, altura_total_pdf))

            y_atual = altura_total_pdf - altura_adesivo

            for i in range(1, quantidade + 1):
                adesivo_atual = imagem_base_rgba.copy()
                codigo_atual = f"{codigo_base}-{i:06d}"
                qrcode_img = qrcode.make(codigo_atual).convert("RGBA")

                paste_logo_on_image(adesivo_atual, logo_rgba)
                paste_qrcode_on_image(adesivo_atual, qrcode_img)
                draw_text_on_image(adesivo_atual, codigo_atual)

                with io.BytesIO() as buffer_adesivo_temp:
                    adesivo_atual.save(buffer_adesivo_temp, 'PNG')
                    buffer_adesivo_temp.seek(0)
                    p.drawImage(buffer_adesivo_temp, 0, y_atual, width=largura_rolo, height=altura_adesivo, mask='auto')
                y_atual -= (altura_adesivo + PDF_VERTICAL_GAP)

            p.save()
            pdf_buffer.seek(0)

            print(f"Tarefa {self.request.id} para PDF concluída com sucesso.")
            return f"PDF gerado com sucesso para o código base {codigo_base}."

    except FileNotFoundError:
        print(f"Erro Crítico: O arquivo de imagem base ou a fonte não foram encontrados.")
        return "Falha: Arquivos essenciais não encontrados no servidor."
    except Exception as e:
        print(f"Erro inesperado na tarefa {self.request.id}: {e}")
        raise self.retry(exc=e, countdown=10)

@shared_task(bind=True, max_retries=3)
def criar_zip_qrcodes_async(self: Task, form_data: Dict[str, Any], user_id: int = None) -> str:
    codigo_base = form_data['codigo_base']
    quantidade = form_data['quantidade']

    print(f"Iniciando tarefa de geração de ZIP para {codigo_base} ({quantidade} QR Codes).")

    try:
        try:
            nova_geracao = GeracaoQRCode(codigo=codigo_base, quantidade=quantidade)
            nova_geracao.save()
        except Exception as db_error:
            print(f"Erro CRÍTICO ao salvar registro no DB: {db_error}. Abortando tarefa.")
            return f"Falha ao registrar a geração para {codigo_base}."

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for i in range(1, quantidade + 1):
                codigo_completo = f"{codigo_base}-{str(i).zfill(6)}"
                qr_image = qrcode.make(codigo_completo)

                img_io = io.BytesIO()
                qr_image.save(img_io, format='PNG')
                img_io.seek(0)

                nome_arquivo = f"{codigo_completo}.png"
                zip_file.writestr(nome_arquivo, img_io.read())

        zip_buffer.seek(0)

        print(f"Tarefa {self.request.id} para ZIP concluída com sucesso.")
        return f"Arquivo ZIP gerado com sucesso para o código base {codigo_base}."

    except Exception as e:
        print(f"Erro inesperado na tarefa {self.request.id}: {e}")
        raise self.retry(exc=e, countdown=10)
