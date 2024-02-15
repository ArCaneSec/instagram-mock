from datetime import date

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.authenticate import authenticate

from . import core
from . import models as m
from . import serializers as s


@api_view(["POST", "PUT"])
@authenticate
def upload(request):
    """
    This view is responsible for uploading files related to posts,
    'PUT' method must be used for uploading,

    Successfully uploaded file will get an associated id that must
    be used in post creation api.

    Request body schema:
        'content' (str): file content.
    """

    UPLOAD_CAPACITY = 10

    if request.method == "PUT":
        serializer = s.UploadPostFileSerializer(data=request.FILES)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        post_file_validator = core.PostFileValidator(
            request.user, UPLOAD_CAPACITY, date.today()
        )
        post_file = core.PostFile(
            **serializer.validated_data, validator=post_file_validator
        )
        if not post_file.validator.is_valid():
            return Response(
                post_file.validator.errors, status.HTTP_400_BAD_REQUEST
            )

        id = post_file.upload_file()
        return Response(
            {
                "message": "file successfully uploaded.",
                "id": id,
                "capacity": UPLOAD_CAPACITY,
                "totalUploads": m.PostFile.specific_date_uploads(
                    request.user, date.today()
                ),
            },
            status.HTTP_201_CREATED,
        )

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
    """
    Responsible for liking an specific post, as well as removing it.
    Post id is fetched from path parameters.
    """

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
        delete_post_like_processor = core.RemovePostLike(request.user, post_id)
        if not delete_post_like_processor.is_valid():
            return Response(
                delete_post_like_processor.errors, status.HTTP_400_BAD_REQUEST
            )

        delete_post_like_processor.remove_like()
        return Response(
            {"message": "like removed successfully."}, status.HTTP_200_OK
        )
