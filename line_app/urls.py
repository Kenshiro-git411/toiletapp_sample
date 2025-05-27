from django.urls import path
from . import views

# app_name = 'line_app'

urlpatterns = [
    path('callback/', views.callback, name='callback'),
]