from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError
from django.core.cache import cache
from django.views.decorators.cache import cache_page


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
@permission_classes([IsAuthenticated])
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

@api_view(['GET'])
@cache_page(60 * 15)  # Cache this view for 15 minutes
def cached_view(request):
    # This is just an example of a view that uses Django's cache_page decorator
    return Response({'message': 'This response is cached for 15 minutes'})
