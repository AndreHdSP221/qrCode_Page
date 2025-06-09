from django.urls import path
from . import views

urlpatterns = [
    path('', views.gerar_zip_qrcodes, name='gerar_zip_qrcodes'), # Substituir home por um menu
    path('arbomonitor/', views.gerar_adesivos_arbo, name='AdesivosArbo'),
]
