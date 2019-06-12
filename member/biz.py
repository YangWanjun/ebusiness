from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import connection
from django.db.models import Max, Q
from django.utils import timezone

from . import models, serializers
from utils import common, constants
from utils.errors import CustomException


def get_me(user):
    """ログイン情報を取得

    :param user:
    :return:
    """
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
    members = []
    if not keyword:
        return members
    with connection.cursor() as cursor:
        cursor.callproc('sp_search_member', (keyword,))
        results = common.dictfetchall(cursor)
    # ＩＤ重複したデータを消す
    for item in results:
        if len(members) > 0 and item.get('id') == members[-1].get('id'):
            members.pop()
        members.append(item)
    return members


def get_member_list(date=timezone.now().date()):
    """基準日時の社員メンバー一覧を取得

    :param date:
    :return:
    """
    def set_detail_url(x):
        x['url'] = '/member/{pk}'.format(pk=x.get('id'))
        return x

    with connection.cursor() as cursor:
        cursor.callproc('sp_member_list', (date,))
        results = common.dictfetchall(cursor)
    members = list(map(set_detail_url, results))
    return members


def get_project_history(member_id):
    """社員の案件履歴を取得

    :param member_id:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_project_dashboard', (member_id,))
        results = common.dictfetchall(cursor)
    projects = []
    prev_p = None
    for p in results:
        p['url'] = '/project/{pk}'.format(pk=p.get('id'))
        if prev_p is None:
            projects.append(p)
        elif p.get('id') != prev_p.get('id'):
            projects.append(p)
        else:
            if common.add_days(prev_p.get('end_date')) == p.get('start_date'):
                prev_p['end_date'] = p.get('end_date')
            else:
                projects.append(p)
        prev_p = p
    return projects


def get_organization_history(member_id):
    """社員の所属部署履歴

    :param member_id:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_organization_dashboard', (member_id,))
        results = common.dictfetchall(cursor)
    return results


def get_salesperson_history(member_id):
    """社員の営業担当履歴

    :param member_id:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_salesperson_history', (member_id,))
        results = common.dictfetchall(cursor)
    return results


def get_organization_list():
    with connection.cursor() as cursor:
        cursor.callproc('sp_organization_list')
        results = common.dictfetchall(cursor)
    for row in results:
        row['url'] = '/organization/{pk}'.format(pk=row.get('id'))
    return results


def get_organization_members(org_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_organization_members', (org_id,))
        results = common.dictfetchall(cursor)
    for row in results:
        if row.get('positions') is None:
            continue
        positions = row.get('positions').split(',')
        row['positions'] = ",".join([
            common.get_choice_name_by_key(constants.CHOICE_POSITION, Decimal(pos)) for pos in positions
        ])
    return results


def get_next_bp_employee_id():
    """自動採番するため、次に使う番号を取得する。

    これは最終的に使う社員番号ではありません。
    実際の番号は追加後の主キーを使って、設定しなおしてから、もう一回保存する 。

    :return: string
    """
    max_id = models.Member.objects.all().aggregate(Max('id'))
    max_id = max_id.get('id__max', None)
    if max_id:
        return 'BP%05d' % (int(max_id) + 1,)
    else:
        return ''


def get_member_salesperson_by_month(member, date):
    """社員の営業員を取得する

    :param member:
    :param date:
    :return:
    """
    try:
        return models.SalespersonPeriod.objects.get(
            Q(end_date__gte=date) | Q(end_date__isnull=True),
            start_date__lte=date,
            member=member,
        ).salesperson
    except ObjectDoesNotExist:
        raise CustomException(constants.ERROR_NO_SALESPERSON.format(name=member))
    except MultipleObjectsReturned:
        raise CustomException(constants.ERROR_MULTI_SALESPERSON.format(name=member))
