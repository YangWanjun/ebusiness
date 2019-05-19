import json
import operator
from functools import reduce

from django.db import connection
from django.db.models import Q

from . import models
from utils import common


def get_project_attendance_list(project_id):
    """案件の月ごと出勤リスト

    :param project_id: 案件ＩＤ
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_project_attendance_list', (project_id,))
        data = common.dictfetchall(cursor)
    for row in data:
        row['url'] = '/project/{pk}/attendance/{year}/{month}'.format(
            pk=project_id,
            year=row['year'],
            month=row['month'],
        )
    return data


def get_project_attendance(project_id, year, month):
    """案件の指定年月の出勤明細

    :param project_id:
    :param year:
    :param month:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_project_attendance', (project_id, year, month))
        data = common.dictfetchall(cursor)
    return data


def get_project_order_list(project_id):
    """案件の注文書一覧

    :param project_id: 案件ＩＤ
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_project_order_list', (project_id,))
        data = common.dictfetchall(cursor)
    for row in data:
        row['projects'] = json.loads(row['projects'])
    return data


def search_project(keyword):
    """案件を検索する

    :param keyword:
    :return:
    """
    queryset = models.Project.objects.all()
    for bit in keyword.split():
        or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in ('name__icontains', 'client__name__icontains')]
        queryset = queryset.filter(reduce(operator.or_, or_queries))
    return queryset
