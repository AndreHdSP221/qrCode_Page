from django.db import models

class GeracaoQRCode(models.Model):
    codigo = models.CharField(max_length=100)
    quantidade = models.PositiveIntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo

class adesivosArbo(models.Model):
    codigo = models.CharField(max_length=50)
    quantidade = models.PositiveIntegerField()
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.codigo