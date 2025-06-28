from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Manter vazio essa classe... De acordo com a documentação é necessario essa class. NÃO MUDAR PLMDS.
    pass

admin.site.register(CustomUser, CustomUserAdmin)
