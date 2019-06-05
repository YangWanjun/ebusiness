from django.db import connection
from django.utils import timezone

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
    for row in results:
        row['url'] = '/partner/{partner_id}/members/{member_id}'.format(
            partner_id=partner_id,
            member_id=row.get('id')
        )
    return results


def get_partner_members_order_status(partner_id):
    """協力会社社員の注文状況

    :param partner_id:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_member_orders', (partner_id, timezone.now().today()))
        results = common.dictfetchall(cursor)
    for row in results:
        row['url'] = '/partner/{partner_id}/members/{member_id}/orders'.format(
            partner_id=partner_id,
            member_id=row.get('id')
        )
    return results


def get_partner_member_orders(member_id):
    """協力社員の注文書を取得する

    :param member_id:
    :return:
    """
    member = models.Member.objects.get(pk=member_id)
    qs_project_members = member.projectmember_set.all().order_by('-start_date', '-end_date')
    results = []
    for project_member in qs_project_members:
        results.append({
            'id': project_member.pk,
            'name': project_member.project.name,
            'business_days': None,
            'order_no': '{}～{}'.format(project_member.start_date, project_member.end_date),
            'order_file': None,
            'order_request_file': None,
            'is_sent': None,
            'parent': None,
        })
        orders = []
        for order in project_member.bpmemberorder_set.filter(is_deleted=False):
            orders.append({
                'id': '{}_{}{}'.format(project_member.pk, order.year, order.month),
                'name': '{}年{}月'.format(order.year, order.month),
                'year': order.year,
                'month': order.month,
                'end_year': order.end_year,
                'end_month': order.end_month,
                'business_days': None,
                'order_no': order.order_no,
                'order_file': order.filename,
                'order_request_file': order.filename_request,
                'is_sent': order.is_sent,
                'parent': project_member.pk,
            })
        for year, month in common.get_year_month_list(project_member.start_date, project_member.end_date, True):
            tmp_ls = list(filter(
                lambda i: (i['year'] + i['month']) <= (year + month) <= (i['end_year'] + i['end_month']),
                orders
            ))
            if tmp_ls:
                results.extend(tmp_ls)
            else:
                results.append({
                    'id': '{}_{}{}'.format(project_member.pk, year, month),
                    'name': '{}年{}月'.format(year, month),
                    'year': year,
                    'month': month,
                    'parent': project_member.pk,
                })
    return results
