from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.authenticate import authenticate

from . import serializers as s


@api_view(["POST"])
@authenticate
def upload(request):
    serializer = s.CreatePostSerializer(
        data=request.data, context={"request": request}
    )
    if not serializer.is_valid():
        return Response(
            {"error": serializer.errors},
            status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return Response(
        {"message": "Post created successfully."}, status.HTTP_201_CREATED
    )
