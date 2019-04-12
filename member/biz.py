from django.db import connection

from . import models
from utils import common


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


def search_member_by_name(keyword):
    """名前によってメンバーを検索する

    :param keyword: 名前またはその一部
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_search_member', (keyword,))
        results = common.dictfetchall(cursor)
    # ＩＤ重複したデータを消す
    members = []
    for item in results:
        if len(members) > 0 and item.get('id') == members[-1].get('id'):
            members.pop()
        members.append(item)
    return members
