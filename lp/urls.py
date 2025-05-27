from django.urls import path
from . import views

app_name = 'lp'

urlpatterns = [
    path('', views.display_lp, name='display_lp'),
]