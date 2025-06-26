from django.contrib import admin
from django.urls import path, include 
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='accounts:login', permanent=False), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('qrcode/', include('qrCodeInit.urls', namespace='qrCodeInit')),
]