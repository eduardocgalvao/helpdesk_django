from django.contrib.auth.models import AbstractUser
from django.conf import settings

from django.db import models



class User(AbstractUser):
    pass


class Tickets(models.Model):
    equipamento = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    data_abertura = models.DateField(auto_now_add=True, null=False, blank=False)
    data_fechamento = models.DateField()
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chamados'
    )
    status = models.ForeignKey(
        'Status',
        on_delete=models.CASCADE,
        related_name='chamados'
    )

class Status(models.Model):
    status_name = models.CharField(max_length=50)
    

