from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import date

from django.db import models



class User(AbstractUser):
    pass




class Tickets(models.Model):
    equipamento = models.CharField(max_length=50)
    description = models.TextField(max_length=200)
    data_abertura = models.DateField(auto_now_add=True, null=False, blank=False)
    data_fechamento = models.DateField(null=True, blank=True)

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ticket_usuario'
    )
    
    status = models.ForeignKey(
        'Status',
        on_delete=models.CASCADE,
        related_name='ticket_status'
    )

    def mark_has_complete(self):
        if not self.data_fechamento:
            self.data_fechamento = date.today()
            self.save()

class Status(models.Model):
    status_name = models.CharField(max_length=50)

    def __str__(self):
        return self.status_name
    

    

