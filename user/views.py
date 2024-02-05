from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import serializers as s

# Create your views here.


@api_view(["POST"])
def sign_up(request):
    serializer = s.SignUpRequest(request.data)
    if not serializer.is_valid():
        return Response("Invalid request.")
