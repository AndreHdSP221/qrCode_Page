from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_user, name='login'),
    path('creataccount/', views.create_a_account_view, name='creataccount'),
    path('verify-2fa/', views.verify_2fa_view, name='verify_2fa'),
    path('logout/', views.logout_view, name='logout'),
    path('verify-action/<uuid:token>/', views.verify_action, name='verify_action'),
]
