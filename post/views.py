from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.authenticate import authenticate

from . import core
from . import serializers as s


@api_view(["POST"])
@authenticate
def upload(request):
    serializer = s.CreatePostSerializer(
        data=request.data, context={"request": request}
    )
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status.HTTP_400_BAD_REQUEST,
        )

    serializer.save()
    return Response(
        {"message": "Post created successfully."}, status.HTTP_201_CREATED
    )


@api_view(["PUT", "DELETE"])
@authenticate
def like(request, post_id):
    if request.method == "PUT":
        like_post_proccess = core.LikePostCreate(request.user, post_id)
        if not like_post_proccess.is_valid():
            return Response(
                like_post_proccess.errors, status.HTTP_400_BAD_REQUEST
            )

        like_post_proccess.like_post()
        return Response(
            {"message": "post liked successfully."}, status.HTTP_201_CREATED
        )
    elif request.method == "DELETE":
        delete_post_like_processor = core.LikePostDelete(request.user, post_id)
        if not delete_post_like_processor.is_valid():
            return Response(
                delete_post_like_processor.errors, status.HTTP_400_BAD_REQUEST
            )

        delete_post_like_processor.delete_like()
        return Response(
            {"message": "like removed successfully."}, status.HTTP_200_OK
        )
