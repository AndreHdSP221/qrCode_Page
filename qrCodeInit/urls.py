from django.urls import path
from . import views

urlpatterns = [
    path('', views.gerar_zip_qrcodes, name='gerar_zip_qrcodes'), # Substituir home por um menu com varias opções
]
