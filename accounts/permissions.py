from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse


def user_is_manager(user) -> bool:
    return bool(getattr(user, "is_authenticated", False) and getattr(user, "is_manager", False))


def manager_required(view_func):
    @wraps(view_func)
    def _wrapped(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not user_is_manager(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return _wrapped
