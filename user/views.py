from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import serializers as s

# Create your views here.


@api_view(["POST"])
def sign_up(request):
    serializer = s.SignUpRequest(data=request.data)
    if not serializer.is_valid():
        return Response(
            f"Invalid request.\r\n{serializer.errors}",
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response("Done", status.HTTP_201_CREATED)
