import uuid
import random
from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

class LoginCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='Login_codes')
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)
    
    def is_expired(self) -> bool:
        expiration_time = self.created_at + timedelta(minutes=10)
        return timezone.now() > expiration_time
    
    def __str__(self):
        return f'Código para {self.user.username}'
    

class ActionToken(models.Model):
    """ Mexer aqui caso foi adicionar mais algum tipo de ação """
    class ActionTypes(models.TextChoices):
        ACCOUNT_ACTIVATION = 'ACCOUNT_ACTIVATION', 'Ativação de Conta'
        ACCOUNT_DELETION = 'ACCOUNT_DELETION', 'Exclusão de Conta'
        ACCOUNT_LOGIN = "ACCOUNT_LOGIN", "Login de Conta"
        PASSWORD_RESET = 'PASSWORD_RESET', 'Recuperação de Senha'

    """ Campos da Tab. """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    action_type = models.CharField(max_length=30, choices=ActionTypes.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    """ Verifica se o token expirou """
    def is_expired(self) -> bool:
        expiration_time = self.created_at + timedelta(minutes=30)
        return timezone.now() > expiration_time
    
    def __str__(self):
        return f"Token para {self.user} - Ação: {self.get_action_type_display()}"
    
