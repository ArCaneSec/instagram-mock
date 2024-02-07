from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from . import authenticate as auth
from . import models as m
from . import serializers as s
from . import utils as u

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
    return Response({"message": "Done"}, status.HTTP_201_CREATED)


@api_view(["POST"])
def login(request):
    serializer = s.LoginSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )
    if user := auth.login(**serializer.validated_data):
        res = Response(
            {"message": "successfully logined."}, status.HTTP_200_OK
        )
        token = auth.generate_jwt_token(user, u.generate_expire_date())
        res.set_cookie(
            "token", token, httponly=True, samesite="strict", secure=True
        )
        return res
