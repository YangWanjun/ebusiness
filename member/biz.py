def get_me(user):
    # if user and hasattr(user, 'member'):
    #     member = user.member
    # else:
    #     member = None
    return {
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
    }
