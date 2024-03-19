import datetime
import re
from dataclasses import dataclass, field
from typing import Callable

from rest_framework.serializers import FileField

from comment import models as cm
from user import models as u
from utils.decorators import validation_required
from utils.exceptions import JsonSerializableValueError
from utils.validators import Validator

from . import models as m


@dataclass
class PostValidator(Validator):
    user: u.User
    post_id: int
    _post_obj: m.Post = field(init=False, repr=False)

    def is_valid(self, custom_validators: list[Callable]):
        try:
            self._validate_post()
            [func() for func in custom_validators]

        except JsonSerializableValueError as e:
            self._error = e
            return False

        self._validation_passed = True
        return True

    def _validate_post(self):
        post = m.Post.objects.filter(pk=self.post_id, is_active=True).first()
        if not post:
            raise JsonSerializableValueError(
                {"error": "post not found.", "code": "invalidPost"}
            )
        self._post_obj = post

    def _check_validation_passed(self):
        if not self._validation_passed:
            raise JsonSerializableValueError(
                "You cannot call this function without "
                "running validations first."
            )


@dataclass
class PostLike(PostValidator):

    def is_valid(self):
        return super().is_valid([self._check_user_havent_liked])

    def _check_user_havent_liked(self):
        user_liked = m.PostLikes.objects.filter(
            user=self.user, post=self._post_obj
        ).first()
        if user_liked:
            raise JsonSerializableValueError(
                {
                    "error": "you have already liked this post.",
                    "code": "duplicateLike",
                }
            )

    def like_post(self):
        self._check_validation_passed()
        m.PostLikes.objects.create(user=self.user, post=self._post_obj)


@dataclass
class DeletePostLike(PostValidator):
    _post_like_obj: m.PostLikes = field(init=False, repr=False)

    def is_valid(self):
        return super().is_valid([self._check_user_has_liked])

    def _check_user_has_liked(self):
        user_liked = m.PostLikes.objects.filter(
            user=self.user, post=self._post_obj
        ).first()
        if not user_liked:
            raise JsonSerializableValueError(
                {
                    "error": "you haven't liked this post yet.",
                    "code": "notLiked",
                }
            )
        self._post_like_obj = user_liked

    def remove_like(self):
        self._check_validation_passed()
        self._post_like_obj.delete()


@dataclass
class PostFileValidator:
    user: u.User
    capacity: int = field(default=10)
    date: datetime.date = field(default_factory=datetime.date.today)
    _error_messages: str = field(init=False, repr=False)

    def is_valid(self) -> bool:
        try:
            self._validate_date_total_uploads()
        except JsonSerializableValueError as e:
            self._error_messages = e.message
            return False

        return True

    @property
    def errors(self):
        return self._error_messages

    def _validate_date_total_uploads(self):
        today_files = m.PostFile.objects.filter(
            created_at=self.date, post__isnull=True
        )
        if len(today_files) >= self.capacity:
            raise JsonSerializableValueError(
                {
                    "error": "you have reached the maximum "
                    "number of files for today.",
                    "code": "capacity",
                }
            )


@dataclass
class PostFile:
    content: FileField
    validator: PostFileValidator

    @staticmethod
    def delete_today_files(date: datetime.date) -> None:
        m.PostFile.objects.filter(created_at=date, post__isnull=True).delete()

    def upload_file(self) -> int:
        if not self.validator.is_valid():
            raise ValueError(
                "You cannot call this method without validating data."
            )

        return m.PostFile.objects.create(
            user=self.validator.user,
            content_type=self.content.extension,
            content=self.content,
        ).pk


@dataclass
class AddComment(PostValidator):
    content: str

    def is_valid(self):
        return super().is_valid([self._extract_tags])

    def _extract_tags(self):
        pattern = r"(?:@)([a-z][a-z\d._]{2,250})(?:$| |\n)"
        tags = re.findall(pattern, self.content)
        self.tags = u.User.objects.filter(username__in=tags, is_active=True)

    @validation_required
    def add_comment(self):
        comment = cm.Comment.objects.create(
            user=self.user, post=self._post_obj, content=self.content
        )
        comment.tags.set(self.tags)


@dataclass
class DeleteComment(PostValidator):
    comment_id: int
    _comment: cm.Comment = field(init=False, default=None)

    def is_valid(self):
        return super().is_valid([self._validate_comment])

    def _validate_comment(self):
        self._comment = cm.Comment.objects.filter(
            pk=self.comment_id, user=self.user
        )
        if not self._comment:
            raise JsonSerializableValueError(
                {"error": "comment not found.", "code": "notFound"}
            )

    @validation_required
    def delete_comment(self):
        self._comment.delete()
