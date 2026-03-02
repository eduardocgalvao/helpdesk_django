from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, Tickets, Status


@admin.register(User)
class CustomUserAdmin(UserAdmin):
	pass


@admin.register(Tickets)
class TicketsAdmin(admin.ModelAdmin):
	list_display = ("id", "equipamento", "status", "usuario", "data_abertura", "data_fechamento")
	list_filter = ("status", "data_abertura")
	search_fields = ("equipamento", "description", "usuario__username")
	readonly_fields = ("data_abertura", "data_fechamento", "comment")


@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
	list_display = ("id", "status_name")
	search_fields = ("status_name",)
