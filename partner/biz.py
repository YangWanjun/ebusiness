import datetime

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.contrib.humanize.templatetags import humanize
from django.db import connection
from django.db.models import Q
from django.utils import timezone

from . import models, serializers
from master.models import Config
from member.biz import get_member_salesperson_by_month
from utils import common, constants
from utils.errors import CustomException


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
            orders.append(serializers.BpMemberOrderDisplaySerializer(order).data)
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
                    'end_year': year,
                    'end_month': month,
                    'business_days': len(common.get_business_days(year, month)),
                    'parent': project_member.pk,
                })
    return results


def generate_partner_order_data(
        company, partner, project_member, order_no, year, month, publish_date, end_year=None, end_month=None
):
    if not end_year or not end_month:
        end_year = year
        end_month = month
    elif '%04d%02d' % (int(year), int(month)) > '%04d%02d' % (int(end_year), int(end_month)):
        # 終了年月は開始年月の前の場合エラーとする。
        raise CustomException(constants.ERROR_DELETE_PROTECTED.format(year=end_year, month=end_month))
    interval = (int(end_year) * 12 + int(end_month)) - (int(year) * 12 + int(month)) + 1
    member = project_member.member
    contract = get_partner_member_contract(partner, member, year, month)
    heading = generate_partner_order_heading(
        company, project_member, partner, contract, year, month, publish_date, interval
    )
    order = {'order_no': order_no}
    return {
        'order': order,
        'heading': heading,
    }


def generate_partner_order_heading(
        company, project_member, partner, contract, year, month, publish_date, interval
):
    first_day = common.get_first_day_from_ym(year + month)
    last_day = common.get_last_day_by_month(first_day)
    project = project_member.project
    member = project_member.member
    end_date = last_day if last_day <= project_member.end_date else project_member.end_date
    salesperson = get_member_salesperson_by_month(member, end_date)
    data = dict()
    data['publish_date'] = publish_date.strftime('%Y-%m-%d') \
        if isinstance(publish_date, (datetime.date, datetime.datetime)) else publish_date
    data['partner_name'] = partner.name
    data['partner_post_code'] = partner.post_code
    data['partner_address1'] = partner.address1
    data['partner_address2'] = partner.address2
    data['partner_tel'] = partner.tel
    data['partner_fax'] = partner.fax
    # 本社情報
    data['company_name'] = company.name
    data['company_tel'] = company.tel
    data['company_address1'] = company.address1
    data['company_address2'] = company.address2
    # 案件情報
    data['project_name'] = project.name
    data['start_date'] = first_day if first_day >= project_member.start_date else project_member.start_date
    data['end_date'] = end_date
    data['master'] = company.president
    data['middleman'] = salesperson.full_name
    data['partner_master'] = partner.president
    data['partner_middleman'] = partner.middleman
    data['member_name'] = member.full_name
    data['location'] = project.address if project.address else constants.LABEL_BP_ORDER_DEFAULT_LOCATION
    # 精算情報
    data['is_hourly_pay'] = contract.is_hourly_pay
    data['is_fixed_cost'] = contract.is_fixed_cost
    data['is_show_formula'] = contract.is_show_formula
    data['calculate_type_comment'] = contract.get_calculate_type_comment()
    data['allowance_base'] = contract.get_cost() * interval
    data['allowance_base_memo'] = contract.allowance_base_memo
    if interval > 1:
        data['allowance_base_memo'] = "基本料金：￥{}円  ({}税金抜き)".format(
            humanize.intcomma(data['allowance_base']),
            '固定、' if contract.is_fixed_cost else '',
        )
    data['allowance_time_min'] = contract.get_allowance_time_min(year, month)
    data['allowance_time_max'] = contract.allowance_time_max
    data['allowance_time_memo'] = contract.get_allowance_time_memo(year, month)
    data['allowance_overtime'] = contract.allowance_overtime
    data['allowance_overtime_memo'] = contract.allowance_overtime_memo
    data['allowance_absenteeism'] = contract.get_allowance_absenteeism(year, month)
    data['allowance_absenteeism_memo'] = contract.get_allowance_absenteeism_memo(year, month)
    data['allowance_other'] = contract.allowance_other
    data['allowance_other_memo'] = contract.get_allowance_other_memo()
    data['comment'] = contract.comment
    data['delivery_properties_comment'] = Config.get_bp_order_delivery_properties()
    data['payment_condition_comments'] = Config.get_bp_order_payment_condition()
    data['contract_items_comments'] = Config.get_bp_order_contract_items()
    return data


def get_partner_member_contract(partner, member, year=None, month=None):
    """協力社員の契約を取得

    :param partner: 協力会社
    :param member: 社員
    :param year: 対象年
    :param month: 対象月
    :return:
    """
    try:
        first_day = common.get_first_day_from_ym(year + month)
        last_day = common.get_last_day_by_month(first_day)
        return models.BpContract.objects.get(
            Q(end_date__gte=first_day) | Q(end_date__isnull=True),
            start_date__lte=last_day,
            company=partner,
            member=member,
        )
    except ObjectDoesNotExist:
        raise CustomException(constants.ERROR_NO_PARTNER_CONTRACT.format(name=member, company=partner))
    except MultipleObjectsReturned:
        raise CustomException(constants.ERROR_MULTI_PARTNER_CONTRACT.format(name=member, company=partner))


def get_partner_lump_contracts(partner_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_partner_lump_orders', (partner_id,))
        results = common.dictfetchall(cursor)
    for row in results:
        row['order_url'] = '/partner/{partner_id}/order/{order_id}'.format(
            partner_id=partner_id,
            order_id=row['order_id']
        )
    return results
