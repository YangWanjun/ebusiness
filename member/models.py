import datetime

from django.db import models
from django.db.models import PROTECT

from master.models import Bank, BankBranch
from utils import constants
from utils.models import BaseModel, AbstractMember


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
    pay_bank = models.ForeignKey(Bank, blank=True, null=True, on_delete=PROTECT, verbose_name="銀行")
    pay_branch = models.ForeignKey(BankBranch, blank=True, null=True, on_delete=PROTECT, verbose_name="銀行支店")
    pay_owner = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義")
    pay_owner_kana = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義（カナ）")
    pay_account = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座番号")
    avatar_url = models.CharField(blank=True, null=True, max_length=500, verbose_name="自分の写真")

    class Meta:
        db_table = 'eb_member'
        verbose_name = "社員"
        verbose_name_plural = "社員一覧"

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        return '{} {}'.format(self.last_name, self.first_name)

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')


class Organization(BaseModel):
    name = models.CharField(max_length=30, blank=False, null=False, verbose_name="組織名")
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name="概要")
    org_type = models.CharField(
        blank=False, null=False, max_length=2, choices=constants.CHOICE_ORG_TYPE, verbose_name="組織類別"
    )
    parent = models.ForeignKey(
        "self", related_name='children', blank=True, null=True, on_delete=PROTECT, verbose_name="親組織"
    )
    members = models.ManyToManyField(Member, through='Membership')

    class Meta:
        db_table = 'eb_organization'
        verbose_name = "組織"
        verbose_name_plural = "組織一覧"

    def __str__(self):
        return self.name


class Membership(BaseModel):
    member = models.ForeignKey(Member, on_delete=PROTECT, verbose_name="社員")
    organization = models.ForeignKey(Organization, on_delete=PROTECT, verbose_name="組織")
    start_date = models.DateField(verbose_name="開始日")
    end_date = models.DateField(default=datetime.date.max, verbose_name="終了日")

    class Meta:
        db_table = 'eb_membership'
        verbose_name = "所属"
        verbose_name_plural = "所属一覧"
