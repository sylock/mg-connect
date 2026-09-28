def navigation(request):
    user = request.user
    is_manager = bool(getattr(user, "is_authenticated", False) and getattr(user, "is_manager", False))
    return {
        "nav_is_manager": is_manager,
        "nav_user_label": (
            (user.display_name or user.get_username())
            if getattr(user, "is_authenticated", False)
            else ""
        ),
    }
