import os
import re
import calendar
import datetime
import math
import pytz
import logging
from urllib.parse import urlparse

from . import jholiday, constants


def get_tz_utc():
    return pytz.utc


def get_system_logger():
    """システムのロガーを取得する。

    :return:
    """
    return logging.getLogger('system')


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict

    :param cursor:
    :return:
    """
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def to_relative_url(absolute_url):
    """絶対URLを相対URLに変換

    :param absolute_url:
    :return:
    """
    result = urlparse(absolute_url)
    return result.path


def choices_to_dict_list(choices):
    """

    :param choices:
    :return:
    """
    if not choices:
        return None
    results = []
    for k, v in choices:
        results.append({
            'value': k,
            'display_name': v
        })
    return results


def get_full_postcode(postcode):
    if postcode and re.match(r'^\d+$', postcode):
        return "%s-%s" % (postcode[:3], postcode[3:])
    else:
        return postcode


def add_days(source_date, days=1):
    return source_date + datetime.timedelta(days=days)


def add_months(source_date, months=1):
    month = source_date.month - 1 + months
    year = int(source_date.year + month / 12)
    month = month % 12 + 1
    day = min(source_date.day, calendar.monthrange(year, month)[1])
    return datetime.date(year, month, day)


def get_first_day_by_month(source_date):
    return datetime.date(source_date.year, source_date.month, 1)


def get_last_day_by_month(source_date):
    next_month = add_months(source_date, 1)
    return next_month + datetime.timedelta(days=-next_month.day)


def get_first_day_from_ym(ym):
    if re.match(r"^[0-9]{6}$", ym):
        try:
            return datetime.date(int(ym[:4]), int(ym[4:]), 1)
        except ValueError:
            return None
    else:
        return None


def get_last_day_from_ym(ym):
    first_day = get_first_day_from_ym(ym)
    if first_day:
        return get_last_day_by_month(first_day)
    else:
        return None


def get_consumption_tax(amount, tax_rate, decimal_type):
    """消費税を取得する。

    :param amount:
    :param tax_rate:
    :param decimal_type:
    :return:
    """
    if not amount:
        return 0
    return get_integer(amount * tax_rate, decimal_type)


def get_integer(value, decimal_type):
    """小数がある場あるの処理方法

    :param value:
    :param decimal_type:
    :return:
    """
    if value:
        if decimal_type == '0':
            # 切り捨て
            return math.floor(value)
        elif decimal_type == '1':
            # 四捨五入
            return round(value)
        elif decimal_type == '2':
            # 切り上げ
            return math.ceil(value)
    else:
        return 0


def get_business_days(year, month, exclude=None):
    from master.models import Holiday
    business_days = []
    eb_holidays = [holiday.date for holiday in Holiday.objects.public_all()]
    for i in range(1, 32):
        try:
            this_date = datetime.date(int(year), int(month), i)
        except ValueError:
            break
        if this_date.weekday() < 5 and jholiday.holiday_name(int(year), int(month), i) is None:
            # Monday == 0, Sunday == 6
            if exclude and this_date.strftime("%Y/%m/%d") not in exclude:
                business_days.append(this_date)
            elif exclude is None:
                business_days.append(this_date)
    return [date for date in business_days if date not in eb_holidays]


def get_request_filename(request_no, request_name, ext='.xlsx'):
    """生成された請求書のパスを取得する。

    :param request_no: 請求番号
    :param request_name: 請求名称
    :param ext: 拡張子
    :return:
    """

    now = datetime.datetime.now()
    filename = "EB請求書_{request_no}_{name}_{timestamp}".format(
        request_no=request_no,
        name=request_name,
        timestamp=now.strftime("%Y%m%d_%H%M%S%f")
    )
    return filename + ext


# def escape_filename(filename):
#     if filename:
#         return re.sub(r'[<>:"/\|?*]', '', filename)
#     else:
#         return filename


def get_attachment_path(self, filename):
    name, ext = os.path.splitext(filename)
    now = datetime.datetime.now()
    path = os.path.join(now.strftime('%Y'), now.strftime('%m'))
    return os.path.join(path, self.uuid + ext)
