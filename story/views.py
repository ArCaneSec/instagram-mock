from datetime import datetime, timedelta

from django.shortcuts import get_object_or_404
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


@api_view(["GET"])
@authenticate
def get_story(request, story_id):
    now = datetime.now()
    story_obj = get_object_or_404(m.Story, pk=story_id, active_until__gt=now)
    if story_obj.user == request.user:
        return Response(
            s.FullStorySerializer(story_obj).data, status.HTTP_200_OK
        )

    if story_obj.user.is_private:
        if not story_obj.user.followers.filter(pk=request.user.pk).first():
            return Response(status=status.HTTP_403_FORBIDDEN)

    if story_obj.privacy_type == m.Story.PrivacyType.CLOSE_FRIEND:
        if not story_obj.user.close_friends.filter(pk=request.user.pk).first():
            return Response(status=status.HTTP_403_FORBIDDEN)

    if not story_obj.views.filter(pk=request.user.pk):
        story_obj.views.add(request.user)
    
    serializer = s.StorySerializer(story_obj)
    return Response(serializer.data, status.HTTP_200_OK)
