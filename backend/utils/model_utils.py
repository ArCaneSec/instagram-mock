from django.conf import settings


def generate_path(instance, filename):
    return (
        settings.STATICFILES_DIRS[0]
        / "users"
        / instance.__class__.__name__.lower()
        / filename
    )
