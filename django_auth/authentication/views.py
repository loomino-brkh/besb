from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import LocalhostOnly
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache


@api_view(['POST'])
def login(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        })
    return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated, LocalhostOnly])
def verify_token(request):
    user_id = request.user.id
    cache_key = f'token_valid_{user_id}'

    # Check if the result is cached
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        return Response({'status': 'valid', 'cached': True})

    # If not cached, perform verification logic here
    # For simplicity, we're just caching the fact that the token is valid
    cache.set(cache_key, True, timeout=300)  # Cache for 5 minutes

    return Response({'status': 'valid', 'cached': False})

@api_view(['POST'])
def refresh_token(request):
    refresh_token = request.data.get('refresh')
    if not refresh_token:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Rate limiting: Allow only 5 refresh attempts per token in 15 minutes
    cache_key = f'refresh_attempt_{refresh_token[:32]}'  # Use first 32 chars of token as key
    attempts = cache.get(cache_key, 0)
    if attempts >= 5:
        return Response({
            'error': 'Too many refresh attempts. Please wait before trying again.'
        }, status=status.HTTP_429_TOO_MANY_REQUESTS)
    
    try:
        refresh = RefreshToken(refresh_token)
        # Increment the attempts counter
        cache.set(cache_key, attempts + 1, timeout=60 * 15)  # 15 minutes expiry
        
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh)  # New refresh token
        })
    except TokenError:
        return Response({
            'error': 'Invalid or expired refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as e:
        return Response({
            'error': 'An error occurred while refreshing token'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
