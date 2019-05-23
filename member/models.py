import datetime

from django.db import models
from django.db.models import PROTECT

from utils import constants
from utils.models import BaseModel, AbstractMember, BaseView


class Member(AbstractMember):
    is_unofficial = models.BooleanField(default=False, verbose_name="内定")
    id_number = models.CharField(blank=True, null=True, max_length=20, verbose_name="在留カード番号")
    id_card_expired_date = models.DateField(blank=True, null=True, verbose_name="在留カード期限")
    visa_start_date = models.DateField(blank=True, null=True, verbose_name="ビザ有効期限（開始）")
    visa_expire_date = models.DateField(blank=True, null=True, verbose_name="ビザ有効期限（終了）")
    passport_number = models.CharField(blank=True, null=True, max_length=20, verbose_name="パスポート番号")
    passport_expired_dt = models.DateField(blank=True, null=True, verbose_name="パスポート有効期限")
    residence_type = models.CharField(
        blank=True, null=True, max_length=20, choices=constants.CHOICE_RESIDENCE_TYPE, verbose_name="在留種類"
    )
    # pay_bank = models.ForeignKey(Bank, blank=True, null=True, on_delete=PROTECT, verbose_name="銀行")
    # pay_branch = models.ForeignKey(BankBranch, blank=True, null=True, on_delete=PROTECT, verbose_name="銀行支店")
    pay_owner = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義")
    pay_owner_kana = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義（カナ）")
    pay_account = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座番号")
    avatar_url = models.CharField(blank=True, null=True, max_length=500, verbose_name="自分の写真")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_member'
        default_permissions = ()
        verbose_name = "社員"
        verbose_name_plural = "社員一覧"

    def __str__(self):
        return self.full_name


class Organization(BaseModel):
    name = models.CharField(max_length=30, blank=False, null=False, verbose_name="部署名")
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name="概要")
    is_on_sales = models.BooleanField(blank=False, null=False, default=False, verbose_name="営業対象")
    is_active = models.BooleanField(default=False, verbose_name="社員に表示")
    parent = models.ForeignKey(
        "self", related_name='children', blank=True, null=True, on_delete=models.PROTECT,
        verbose_name="親組織"
    )
    org_type = models.CharField(
        max_length=2, blank=False, null=False, choices=constants.CHOICE_ORG_TYPE,
        verbose_name="組織類別"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_section'
        default_permissions = ()
        ordering = ('name',)
        verbose_name = "組織"
        verbose_name_plural = "組織一覧"

    def __str__(self):
        return self.name


class OrganizationPeriod(BaseModel):
    member = models.ForeignKey(Member, on_delete=PROTECT, verbose_name="社員")
    division = models.ForeignKey(
        Organization, on_delete=models.PROTECT, blank=True, null=True,
        related_name='divisionperiod_set',
        verbose_name="事業部"
    )
    department = models.ForeignKey(
        Organization, blank=True, null=True, db_column='section_id', on_delete=models.PROTECT, verbose_name="部署"
    )
    section = models.ForeignKey(
        Organization, blank=True, null=True, db_column='subsection_id', on_delete=models.PROTECT,
        related_name='sectionperiod_set',
        verbose_name="課"
    )
    start_date = models.DateField(verbose_name="開始日")
    end_date = models.DateField(default=datetime.date.max, verbose_name="終了日")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_membersectionperiod'
        default_permissions = ()
        verbose_name = "所属"
        verbose_name_plural = "所属一覧"


class SearchMember(BaseView):
    name = models.CharField(max_length=50, verbose_name="名前")
    member_type = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_MEMBER_TYPE, verbose_name="雇用形態"
    )
    join_date = models.DateField(blank=True, null=True, verbose_name='入社年月日')
    end_date = models.DateField(blank=True, null=True, verbose_name='契約終了日')
    salesperson_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="営業ＩＤ")
    salesperson_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="営業員")
    division_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="事業部ＩＤ")
    division_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="事業部")
    department_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="部署ＩＤ")
    department_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="部署")
    section_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="課ＩＤ")
    section_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="課")
    partner_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="協力会社ＩＤ")
    partner_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="協力会社")

    class Meta:
        managed = False
        default_permissions = ()
        verbose_name = "メンバー"
        verbose_name_plural = "メンバー一覧"
