from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='account:login'), name='root_redirect'),
    path('admin/', admin.site.urls),
    path('account/', include('accounts.urls'), name="account"),
    path('qrcode/', include('qrCodeInit.urls'), name="qrcode"),
]
