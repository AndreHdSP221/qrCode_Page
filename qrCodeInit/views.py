
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from .forms import GeradorAdesivosForm, GeradorQrCodeZipForm
from .tasks import criar_pdf_adesivos_async, criar_zip_qrcodes_async

def gerar_adesivos_arbo(request: HttpRequest) -> HttpResponse:
    template_name = 'qrcodetpl/pages/pageadesivoarbo.html'

    if request.method == 'POST':
        form = GeradorAdesivosForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            
            logo_file = cleaned_data.pop('logo') 
            
            logo_content: bytes = logo_file.read()
            
            user_id = request.user.id if request.user.is_authenticated else None

            criar_pdf_adesivos_async.delay(
                form_data=cleaned_data, 
                logo_content=logo_content, 
                user_id=user_id
            )
            
            messages.success(request, 'Sua solicitação foi recebida! O arquivo PDF está sendo gerado.')
            return render(request, template_name, {'form': GeradorAdesivosForm()})
    else:
        form = GeradorAdesivosForm()
        
    return render(request, template_name, {'form': form})

def gerar_zip_qrcodes(request: HttpRequest) -> HttpResponse:
    template_name = 'qrcodetpl/pages/qrCodeSequencial.html'
    
    if request.method == 'POST':
        form = GeradorQrCodeZipForm(request.POST)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            user_id = request.user.id if request.user.is_authenticated else None

            criar_zip_qrcodes_async.delay(
                form_data=cleaned_data,
                user_id=user_id
            )

            messages.success(
                request,
                'Sua solicitação foi recebida! O arquivo .ZIP com os QR Codes está sendo '
                'gerado. Você será notificado em breve.'
            )
            
            return render(request, template_name, {'form': GeradorQrCodeZipForm()})

    else:
        form = GeradorQrCodeZipForm()

    return render(request, template_name, {'form': form})