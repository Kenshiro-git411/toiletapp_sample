from django.urls import path
from . import views

app_name = 'toilet'

urlpatterns = [
    path('', views.liff_entrypoint, name='liff_entry'),
    path('home/', views.home, name='home'),
    path('search_toilet/', views.search_toilet, name='search_toilet'),
    path('suggest_station/', views.suggest_station, name='suggest_station'),
    path('toilet_info/<int:pk>/<int:gender>', views.toilet_info, name='toilet_info'),
    path('change_toilet_data/<int:toilet_pk>/<int:gender_num>/', views.change_toilet_data, name='change_toilet_data'),
    path('toilet_review/<int:toilet_id>/<int:gender>/', views.toilet_review, name='toilet_review'),
    path('toilet_rank/', views.toilet_rank, name='toilet_rank'),
    path('get_toilet_object_rank/<int:line>/<int:gender>/', views.get_toilet_object_rank, name='get_toilet_object_rank'),
    path('get_latest_comment/', views.get_latest_comment, name='get_latest_comment'),
    path('user_comments/', views.user_comments, name="user_comments"),
    path('toilet_review_revise/<int:pk>/<int:gender>/', views.toilet_review_revise, name='toilet_review_revise'),
    path('toilet_review_delete/<int:pk>/<int:gender>/', views.toilet_review_delete, name='toilet_review_delete'),
]