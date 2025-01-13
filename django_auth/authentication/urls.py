from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify/', views.verify_token, name='verify'),
    path('cached/', views.cached_view, name='cached_view'),
]
