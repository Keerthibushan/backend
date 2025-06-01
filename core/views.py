import os
import requests
from django.http import JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from google_auth_oauthlib.flow import Flow

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Record
from .serializers import RecordSerializer

# Base directory of the Django project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Allow insecure transport (HTTP) during development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Setup Google OAuth flow
flow = Flow.from_client_secrets_file(
    os.path.join(BASE_DIR, 'credentials.json'),
    scopes=[
        'https://www.googleapis.com/auth/userinfo.profile',
        'https://www.googleapis.com/auth/userinfo.email',
        'openid'
    ],
    redirect_uri='http://localhost:8000/core/callback'
)

# Step 1: Redirect user to Google OAuth
def google_login(request):
    auth_url, _ = flow.authorization_url(prompt='consent')
    return redirect(auth_url)

# Step 2: Handle the OAuth callback and return tokens
def callback(request):
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Access Token and Refresh Token
    access_token = credentials.token
    refresh_token = credentials.refresh_token

    # You can optionally fetch user profile info
    user_info = requests.get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        params={'alt': 'json'},
        headers={'Authorization': f'Bearer {access_token}'}
    ).json()

    return JsonResponse({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_info': user_info
    })


# Authenticated POST API to add a record
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_record(request):
    serializer = RecordSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(user=request.user)
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)

# Authenticated GET API to fetch records (filtered by title if given)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_records(request):
    title = request.GET.get('title')  # Optional query param
    records = Record.objects.filter(user=request.user)
    if title:
        records = records.filter(title__icontains=title)
    serializer = RecordSerializer(records, many=True)
    return Response(serializer.data)
