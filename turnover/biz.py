from django.db import connection

from . import models
from utils import constants


def get_turnover_monthly_chart():
    with connection.cursor() as cursor:
        cursor.execute('select month, turnover_amount '
                       '  from ('
                       '	select year'
                       '		 , month'
                       '		 , turnover_amount'
                       '	  from v_turnover_monthly'
                       '	 limit 12'
                       '  ) T'
                       ' order by year asc, month asc')
        labels = []
        turnover_amount_list = []
        for row in cursor.fetchall():
            labels.append(constants.DICT_MONTH_EN[row[0]])
            turnover_amount_list.append(row[1])
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
