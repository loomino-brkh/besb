from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify/', views.verify_token, name='verify'),
    path('cached/', views.cached_view, name='cached_view'),
    path('apikeys/', views.APIKeyListView.as_view(), name='api_key_list'),
    path('apikeys/create/', views.APIKeyCreateView.as_view(), name='api_key_create'),
    path('apikeys/revoke/<int:pk>/', views.APIKeyRevokeView.as_view(), name='api_key_revoke'),
]
