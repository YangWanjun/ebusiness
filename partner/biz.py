from django.db import connection

from . import models
from utils import common


def get_partner_list():
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_list')
        results = common.dictfetchall(cursor)
    for row in results:
        row['url'] = '/partner/{pk}'.format(pk=row.get('id'))
    return results


def get_partner_employee_choices(partner_id):
    qs = models.PartnerEmployee.objects.filter(
        company_id=partner_id,
    ).order_by('name')
    members = []
    for item in qs:
        members.append({
            'value': item.pk,
            'display_name': item.name,
        })
    return members


def get_partner_monthly_status(partner_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_monthly_status', (partner_id,))
        results = common.dictfetchall(cursor)
    return results


def get_partner_members(partner_id):
    """協力会社の作業メンバー一覧を取得

    :param partner_id: 協力会社ID
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_members', (partner_id,))
        results = common.dictfetchall(cursor)
    return results
