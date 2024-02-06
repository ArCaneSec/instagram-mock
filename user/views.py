from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
import jwt

from . import serializers as s
from . import utils
from . import models as m
# Create your views here.


@api_view(["POST"])
def sign_up(request):
    serializer = s.SignUpRequest(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    serializer.save()
    return Response("Done", status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = s.LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    if m.User.login(**serializer):
        res = Response()
        token = ...
        res.set_cookie("token", )


