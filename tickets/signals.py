from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group

@receiver(post_save, sender=User)
def default_group(sender, instance, created, **kwargs):
    if created:
        group, _ = Group.objects.get_or_create(name='Colaborador')
        instance.groups.add(group)