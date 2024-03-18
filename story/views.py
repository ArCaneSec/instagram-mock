from user.authenticate import authenticate
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from . import serializers as s


@api_view(["POST", "DELETE"])
def story(request):
    if request.method == "POST":
        serializer = s.UploadStorySerializer(request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)