import datetime

from django.db import connection

from . import models
from utils import constants, common


def get_turnover_monthly_chart():
    """最近一年間の月別売上を取得し、画面上のチャートを作成

    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_turnover_monthly_chart')
        labels = []
        turnover_amount_list = []
        for row in cursor.fetchall():
            labels.append(constants.DICT_MONTH_EN[row[1]])
            turnover_amount_list.append(row[2])
    return {
        'labels': labels,
        'series': [turnover_amount_list],
    }


def get_turnover_yearly_chart():
    """年間売上の情報取得

    :return:
    """
    qs = models.TurnoverYearly.objects.all()
    labels = []
    turnover_amount_list = []
    for item in qs:
        labels.append(item.year)
        turnover_amount_list.append(item.turnover_amount)
    return {
        'labels': labels,
        'series': [turnover_amount_list],
    }


def get_turnover_monthly_by_department_chart():
    """部署別、かつ月別の売上情報

    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_turnover_monthly_by_division_chart')
        data = common.dictfetchall(cursor)
    labels = []
    dict_division = dict()
    first_month = None
    for item in data:
        ym = (item.get('year'), item.get('month'))
        if ym not in labels:
            if first_month is None:
                first_month = datetime.date(int(ym[0]), int(ym[1]), 1)
            labels.append(ym)
        division_id = item.get('division_id')
        if division_id not in dict_division:
            interval = (int(ym[0]) * 12 + int(ym[1])) - (first_month.year * 12 + first_month.month)
            dict_division[division_id] = [None] * interval
        division = dict_division[division_id]
        division.append(item.get('turnover_amount', 0))
    return {
        'labels': [constants.DICT_MONTH_EN[m] for y, m in labels],
        'series': dict_division.values(),
    }
