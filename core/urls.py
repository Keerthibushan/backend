from django.urls import path
from .views import google_login, callback, add_record, get_records

urlpatterns = [
    path('login/', google_login, name='google_login'),
    path('callback', callback, name='google_callback'),
    path('add/', add_record, name='add_record'),
    path('fetch/', get_records, name='get_records'),
]
