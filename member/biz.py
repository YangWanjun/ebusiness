from collections import defaultdict


def get_me(user):
    me = {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_superuser': user.is_superuser,
        'is_staff': user.is_staff,
        'is_active': user.is_active,
    }
    return {
        'me': me,
        'perms': user.get_all_permissions(),
    }
