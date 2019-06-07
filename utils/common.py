import os
import re
import calendar
import datetime
import math
import pytz
import logging
import random
import string
from urllib.parse import urlparse

from django.conf import settings

from . import jholiday


def get_tz_utc():
    return pytz.utc


def get_system_logger():
    """システムのロガーを取得する。

    :return:
    """
    return logging.getLogger('system')


def get_temp_path():
    """一時フォルダーを取得する。

    :return:
    """
    path = os.path.join(settings.MEDIA_ROOT, 'temp')
    if not os.path.exists(path):
        os.mkdir(path)
    return path


def get_temp_file(ext):
    """指定拡張子の一時ファイルを取得する。

    :param ext: 拡張子にdotが必要ない（例：「.pdf」の場合「pdf」を渡してください）
    :return:
    """
    temp_root = get_temp_path()
    file_name = "{0}_{1}.{2}".format(
        datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'),
        random.randint(10000, 99999),
        ext
    )
    temp_file = os.path.join(temp_root, file_name)
    return temp_file


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
    eb_holidays = [holiday.date for holiday in Holiday.objects.all()]
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

    filename = "EB請求書_{request_no}_{name}".format(
        request_no=request_no,
        name=escape_filename(request_name),
    )
    return filename + ext


def get_order_file_path(order_no, member_name):
    """協力会社の注文書のパスを取得する。

    :param order_no:
    :param member_name:
    :return:
    """
    filename = "%s_%s.pdf" % (
        order_no,
        escape_filename(member_name),
    )
    return 'EB注文書_' + filename, 'EB注文請書_' + filename


def escape_filename(filename):
    if filename:
        return re.sub(r'[<>:"/\|?*]', '', filename)
    else:
        return filename


def get_attachment_path(self, filename):
    name, ext = os.path.splitext(filename)
    now = datetime.datetime.now()
    path = os.path.join(now.strftime('%Y'), now.strftime('%m'))
    return os.path.join(path, self.uuid + ext)


def get_choice_name_by_key(choices, key):
    """２次元のTupleからキーによって、名称を取得する。

    :param choices:
    :param key:
    :return:
    """
    if choices and key:
        if isinstance(choices, (tuple, list)):
            for k, v in choices:
                if k == key:
                    return v
    return ''


def get_year_month_list(start_date, end_date, is_reverse=False):
    """開始日から終了日までの年月リストを取得する

    :param start_date: 開始日
    :param end_date: 終了日
    :param is_reverse: 降順
    :return:
    """
    if is_reverse:
        temp_date = end_date
        while start_date.strftime('%Y%m') <= temp_date.strftime('%Y%m'):
            yield temp_date.strftime('%Y'), temp_date.strftime('%m')
            temp_date = add_months(temp_date, -1)
    else:
        temp_date = start_date
        while temp_date.strftime('%Y%m') <= end_date.strftime('%Y%m'):
            yield temp_date.strftime('%Y'), temp_date.strftime('%m')
            temp_date = add_months(temp_date)


def join_html(html1, html2):
    """二つのＨＴＭＬを１つに結合する

    :param html1:
    :param html2:
    :return:
    """
    # 二つ目のHTML中で、<body></body>中身の内容を取り出す。
    pattern = re.compile('<body[^<>]*>(.+)</body>', re.MULTILINE | re.DOTALL)
    m = pattern.search(html2)
    if m:
        html2 = m.groups()[0]
    end_body_index = html1.rfind('</body>')
    if end_body_index > 0:
        return html1[:end_body_index] + html2 + '</body></html>'
    else:
        return html1 + html2


def generate_password(length=8):
    """パスワードを作成
    英文字と数字の組み合わせ

    :param length: パスワードの長さ
    :return:
    """
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))
