from django.urls import path
from . import views, apikey_views

urlpatterns = [
    path('login/', views.login, name='login'),
    path('verify/', views.verify_token, name='verify'),
    path('cached/', views.cached_view, name='cached_view'),
    path('apikeys/', apikey_view.APIKeyListView.as_view(), name='api_key_list'),
    path('apikeys/create/', apikey_views.APIKeyCreateView.as_view(), name='api_key_create'),
    path('apikeys/revoke/<int:pk>/', apikey_views.APIKeyRevokeView.as_view(), name='api_key_revoke'),
]
