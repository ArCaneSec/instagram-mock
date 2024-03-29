from datetime import date

from django.shortcuts import get_object_or_404
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
        like_post_proccess = core.PostLike(request.user, post_id)
        if not like_post_proccess.is_valid():
            return Response(
                like_post_proccess.errors, status.HTTP_400_BAD_REQUEST
            )

        like_post_proccess.like_post()
        return Response(
            {"message": "post liked successfully."}, status.HTTP_201_CREATED
        )
    elif request.method == "DELETE":
        delete_post_like_processor = core.DeletePostLike(request.user, post_id)
        if not delete_post_like_processor.is_valid():
            return Response(
                delete_post_like_processor.errors, status.HTTP_400_BAD_REQUEST
            )

        delete_post_like_processor.remove_like()
        return Response(
            {"message": "like removed successfully."}, status.HTTP_200_OK
        )


@api_view(["GET"])
def view_post_anonymously(request, post_id):
    """
    Users can see a public non archived post anonymously from
    this endpoint.
    """

    post = get_object_or_404(
        m.Post, pk=post_id, is_active=True, user__is_private=False
    )
    serializer = s.PostSerializer(post)
    return Response(serializer.data, status.HTTP_200_OK)


@api_view(["PUT", "DELETE"])
@authenticate
def add_comment(request, post_id):
    """
    Responsible for add/delete comment from a post.

    Request schema can be found in 'PostCommentSerializer'.
    Users can add multiple comment on the same post, and can delete
    their own comment.

    Post owners can delete WHATEVER comment they want from their post.
    """

    if request.method == "PUT":
        serializer = s.PostCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        validator = core.AddComment(
            request.user, post_id, **serializer.validated_data
        )
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.add_comment()
        return Response(
            {"message": "comment added successfully."}, status.HTTP_201_CREATED
        )
    else:
        serializer = s.DeletePostCommentSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

        validator = core.DeleteComment(
            request.user, post_id, **serializer.validated_data
        )
        if not validator.is_valid():
            return Response(validator.errors, status.HTTP_400_BAD_REQUEST)

        validator.delete_comment()
        return Response(
            {"message": "comment removed successfully."},
            status.HTTP_200_OK,
        )


@api_view(["GET"])
@authenticate
def view_post(request, post_id):
    """
    Authenticated post viewing, the purpose is to let post owners
    see their archived posts as well, and also post viewers will
    get updated so users won't see duplicate posts in their timeline.
    """

    post = get_object_or_404(m.Post, pk=post_id)
    is_owner = post.user == request.user

    if not post.is_active and not is_owner:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if post.user.is_private:
        if not post.user.followers.filter(pk=request.user.pk):
            return Response(status=status.HTTP_403_FORBIDDEN)

    if not is_owner:
        post.viewers.add(request.user)

    return Response(s.PostSerializer(post).data, status.HTTP_200_OK)
