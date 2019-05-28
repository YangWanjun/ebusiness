from django.db import connection

from utils import common


def get_partner_list():
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_list')
        results = common.dictfetchall(cursor)
    for row in results:
        row['url'] = '/partner/{pk}'.format(pk=row.get('id'))
    return results
