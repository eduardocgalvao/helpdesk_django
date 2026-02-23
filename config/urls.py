"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.contrib.auth.views import LogoutView, LoginView

from tickets.views import(
    TicketListView,
    TicketCreateView,
    TicketUpdateView,
    TicketDeleteView,
    TicketCompleteView,
    SignUpView,
   
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/register/', SignUpView.as_view(), name="register"),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name="logout"),
    path('', TicketListView.as_view(), name="tickets_list"),
    path('create', TicketCreateView.as_view(), name="ticket_form"),
    path('update/<int:pk>', TicketUpdateView.as_view(), name="ticket_update"),
    path('delete/<int:pk>', TicketDeleteView.as_view(), name="ticket_delete"),
    path('complete/<int:pk>', TicketCompleteView.as_view(), name="ticket_complete"),
]
