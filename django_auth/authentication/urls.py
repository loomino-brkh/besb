from django.urls import path
from . import views, apikey_views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify/', views.verify_token, name='verify'),
    path('refresh/', views.refresh_token, name='token_refresh'),
    path('apikeys/', apikey_views.APIKeyListView.as_view(), name='api_key_list'),
    path('apikeys/create/', apikey_views.APIKeyCreateView.as_view(), name='api_key_create'),
    path('apikeys/verify/', apikey_views.APIKeyVerifyView.as_view(), name='api_key_verify'),
    path('apikeys/revoke/<int:pk>/', apikey_views.APIKeyRevokeView.as_view(), name='api_key_revoke'),
    path('user/verify/', views.verify_user, name='verify_user'),
]
