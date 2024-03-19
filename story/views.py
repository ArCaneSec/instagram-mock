from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.authenticate import authenticate

from . import models as m
from . import serializers as s


@api_view(["POST", "DELETE"])
@authenticate
def story(request, story_id=None):
    if request.method == "POST":
        serializer = s.UploadStorySerializer(
            data=request.data, context={"request": request}
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(
            {"message": "story uploaded successfully."},
            status.HTTP_201_CREATED,
        )
    else:
        story = m.Story.objects.filter(pk=story_id, user=request.user).first()
        if not story:
            return Response(
                {"error": "story not found."}, status.HTTP_400_BAD_REQUEST
            )

        story.delete()
        return Response(
            {"message": "story deleted successfully."}, status.HTTP_200_OK
        )
