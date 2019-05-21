import json
import operator
from functools import reduce

from django.contrib.humanize.templatetags import humanize
from django.db import connection
from django.db.models import Q

from . import models, serializers
from utils import common, constants
from utils.errors import CustomException


def get_project_choice(pk_list):
    project_list = []
    for project in models.Project.objects.filter(pk__in=pk_list):
        project_list.append({
            'value': project.pk,
            'display_name': project.name,
        })
    return project_list


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
        if row['request_no']:
            row['request_detail_url'] = '/project/{pk}/request/{request_no}'.format(
                pk=project_id,
                request_no=row['request_no'],
            )
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


def get_request_data(request_no):
    """請求情報を取得

    :param request_no: 請求番号
    :return:
    """
    project_request = models.ProjectRequest.objects.get(request_no=request_no)
    heading = project_request.projectrequestheading
    detail_set = project_request.projectrequestdetail_set.all()
    data = serializers.ProjectRequestSerializer(project_request).data
    data['heading'] = serializers.ProjectRequestHeadingSerializer(heading).data
    data['details'] = serializers.ProjectRequestDetailSerializer(detail_set, many=True).data
    return data


def generate_request_data(company, project, client_order, year, month, initial):
    heading = generate_request_heading(company, project, client_order, year, month, initial)
    details = generate_request_details(project, client_order, year, month, heading)
    heading.update(details['summary'])
    data = {'heading': heading}
    data.update(details)
    return data


def generate_request_heading(company, project, client_order, year, month, initial):
    first_day = common.get_first_day_from_ym(year + month)
    first_day = project.start_date if project.start_date > first_day else first_day
    last_day = common.get_last_day_from_ym(year + month)
    last_day = project.end_date if project.end_date < last_day else last_day
    data = dict()
    # 代表取締役
    data['MASTER'] = company.president
    # お客様郵便番号
    data['CLIENT_POST_CODE'] = common.get_full_postcode(project.client.post_code)
    # お客様住所
    data['CLIENT_ADDRESS'] = (project.client.address1 or '') + (project.client.address2 or '')
    # お客様電話番号
    data['CLIENT_TEL'] = project.client.tel or ''
    # お客様名称
    data['CLIENT_COMPANY_NAME'] = project.client.name
    # 作業期間
    f = '%Y{0}%m{1}%d{2}'
    period_start = first_day.strftime(f).format(*'年月日')
    period_end = last_day.strftime(f).format(*'年月日')
    data['WORK_PERIOD'] = period_start + " ～ " + period_end
    data['WORK_PERIOD_START'] = first_day
    data['WORK_PERIOD_END'] = last_day
    # 注文番号
    if initial and 'order_no' in initial:
        data['ORDER_NO'] = initial.get('order_no')
    else:
        data['ORDER_NO'] = client_order.order_no if client_order.order_no else ""
    # 注文日
    data['REQUEST_DATE'] = client_order.order_date.strftime('%Y/%m/%d') if client_order.order_date else ""
    # 契約件名
    if initial and 'contract_name' in initial:
        data['CONTRACT_NAME'] = initial.get('contract_name')
    else:
        data['CONTRACT_NAME'] = client_order.name
    # お支払い期限
    data['REMIT_DATE'] = project.client.get_pay_date(date=first_day).strftime('%Y/%m/%d')
    data['REMIT_DATE_PURE'] = project.client.get_pay_date(date=first_day)
    # # 請求番号
    # data['REQUEST_NO'] = project.get_next_request_no(year, month)
    # 発行日（対象月の最終日）
    data['PUBLISH_DATE'] = last_day.strftime(f).format(*'年月日')
    data['PUBLISH_DATE_PURE'] = last_day
    # 本社郵便番号
    data['POST_CODE'] = common.get_full_postcode(company.post_code)
    # 本社住所
    data['ADDRESS'] = (company.address1 or '') + (company.address2 or '')
    # 会社名
    data['COMPANY_NAME'] = company.name
    # 本社電話番号
    data['TEL'] = company.tel
    if initial and 'bank_account' in initial:
        bank_account = initial.get('bank_account')
    else:
        bank_account = client_order.bank_account
    data['BANK_ACCOUNT'] = bank_account
    # 振込先銀行名称
    data['BANK_NAME'] = bank_account.bank.name if bank_account else ""
    # 支店番号
    data['BRANCH_NO'] = bank_account.branch_no if bank_account else ""
    # 支店名称
    data['BRANCH_NAME'] = bank_account.branch_name if bank_account else ""
    # 預金種類
    data['ACCOUNT_TYPE'] = bank_account.get_account_type_display() if bank_account else ""
    data['ACCOUNT_TYPE_PURE'] = bank_account.account_type if bank_account else ""
    # 口座番号
    data['ACCOUNT_NUMBER'] = bank_account.account_number if bank_account else ""
    # 口座名義人
    data['BANK_ACCOUNT_HOLDER'] = bank_account.account_holder if bank_account else ""

    return data


def generate_request_details(project, client_order, year, month, heading):
    detail_all = dict()
    detail_members = []
    members_amount = 0
    project_members = get_request_members_in_project(project, client_order, year, month)
    if project.is_lump:
        members_amount = project.lump_amount
        # 番号
        detail_all['NO'] = "1"
        # 項目：契約件名に設定
        detail_all['ITEM_NAME_ATTENDANCE_TOTAL'] = heading['CONTRACT_NAME']
        # 数量
        detail_all['ITEM_COUNT'] = "1"
        # 単位
        detail_all['ITEM_UNIT'] = "一式"
        # 金額
        detail_all['ITEM_AMOUNT_ATTENDANCE_ALL'] = members_amount
        # 備考
        detail_all['ITEM_COMMENT'] = project.lump_comment if project.is_lump and project.lump_comment else ""
        detail_members.append(detail_all)
    else:
        for i, project_member in enumerate(project_members, start=1):
            dict_item = dict()
            # この項目は請求書の出力ではなく、履歴データをProjectRequestDetailに保存するために使う。
            dict_item["EXTRA_PROJECT_MEMBER"] = project_member
            # 番号
            dict_item['NO'] = str(i)
            # 項目
            dict_item['ITEM_NAME'] = str(project_member.member)
            # 時給の場合
            if project.is_hourly_pay:
                # 単価（円）
                dict_item['ITEM_PRICE'] = project_member.hourly_pay or 0
                # Min/Max（H）
                dict_item['ITEM_MIN_MAX'] = ""
            else:
                # 単価（円）
                dict_item['ITEM_PRICE'] = project_member.price or 0
                # Min/Max（H）
                dict_item['ITEM_MIN_MAX'] = "%s/%s" % (project_member.min_hours, project_member.max_hours)
                dict_item.update(project_member.get_attendance_dict(year, month))
            # 金額合計
            members_amount += dict_item['ITEM_AMOUNT_TOTAL']
            detail_members.append(dict_item)

    detail_expenses, expenses_amount = get_request_expenses_list(
        project,
        year,
        month,
        project_members
    )
    tax_amount = common.get_consumption_tax(members_amount, project.client.tax_rate, project.client.decimal_type)

    return {
        'detail_all': detail_all,
        'MEMBERS': detail_members,
        'EXPENSES': detail_expenses,  # 清算リスト
        'summary': {
            'ITEM_AMOUNT_ATTENDANCE': members_amount,
            'ITEM_AMOUNT_ATTENDANCE_TAX': tax_amount,
            'ITEM_AMOUNT_ATTENDANCE_ALL': members_amount + tax_amount,
            'ITEM_AMOUNT_ALL': members_amount + tax_amount + expenses_amount,
            'ITEM_AMOUNT_ALL_COMMA': humanize.intcomma(members_amount + tax_amount + expenses_amount),
            'ITEM_AMOUNT_EXPENSES': expenses_amount,
        },
    }


def get_request_members_in_project(project, client_order, year, month):
    """指定案件の指定注文書の中に、対象のメンバーを取得する。

    :param project: 指定案件
    :param client_order: 指定注文書
    :param year: 対象年
    :param month: 対象月
    :return: メンバーのリスト
    """
    first_day = common.get_first_day_from_ym(year + month)
    last_day = common.get_last_day_by_month(first_day)
    if client_order.projects.filter(is_deleted=False).count() > 1:
        # 一つの注文書に複数の案件がある場合
        projects = client_order.projects.filter(is_deleted=False)
        project_members = models.ProjectMember.objects.filter(
            project__in=projects,
            start_date__lte=last_day,
            end_date__gte=first_day,
            is_deleted=False,
        )
    elif project.clientorder_set.filter(
            start_date__lte=last_day, end_date__gte=first_day, is_deleted=False
    ).count() > 1:
        # １つの案件に複数の注文書ある場合
        raise CustomException(constants.ERROR_NOT_IMPLEMENTED)
    else:
        project_members = project.get_project_members_by_month(year, month)
    return project_members


def get_request_expenses_list(project, year, month, project_members):
    """請求書の精算リストを取得

    :param project: 案件
    :param year: 対象年
    :param month: 対象月
    :param project_members: アサインしたメンバー
    :return:
    """
    dict_expenses = {}
    for expenses in get_project_expenses(project, year, month, project_members):
        if expenses.category.name not in dict_expenses:
            dict_expenses[expenses.category.name] = [expenses]
        else:
            dict_expenses[expenses.category.name].append(expenses)
    detail_expenses = []
    expenses_amount = 0
    for key, value in dict_expenses.items():
        d = dict()
        member_list = []
        amount = 0
        for expenses in value:
            member_list.append(
                expenses.project_member.member.first_name +
                expenses.project_member.member.last_name +
                "￥%s" % (expenses.price,)
            )
            amount += expenses.price
            expenses_amount += expenses.price
        d['ITEM_EXPENSES_CATEGORY_SUMMARY'] = "%s(%s)" % (key, "、".join(member_list))
        d['ITEM_EXPENSES_CATEGORY_AMOUNT'] = amount
        detail_expenses.append(d)
    return detail_expenses, expenses_amount


def get_project_expenses(project, year, month, project_members):
    """指定年月の清算リストを取得する。

    :param project: 案件
    :param year:
    :param month:
    :param project_members:
    :return:
    """
    return models.MemberExpenses.objects.filter(
        project_member__project=project,
        year=str(year),
        month=str(month),
        project_member__in=project_members
    ).order_by(
        'category__name',
    )
