from django.urls import path
from . import views


app_name = 'accounts'

urlpatterns = [
    path('user_login/', views.user_login, name='user_login'),
    path('liff_login/', views.liff_login_view, name='liff_login'),
    path('user_create/', views.user_create, name='user_create'),
    path('user_logout/', views.user_logout, name='user_logout'),
    path('user_info_update/', views.user_info_update, name='user_info_update'),
    path("password-reset/", views.password_reset_request, name="password_reset_request"),
    path("password-reset/done/", views.password_reset_done, name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("password-reset/complete/", views.password_reset_complete, name="password_reset_complete"),
    path("user_delete/", views.user_delete, name="user_delete"),
]