from django.db import models

from master.models import Bank, BankBranch
from utils import constants
from utils.django_base import BaseModel


class Organization(BaseModel):
    name = models.CharField(blank=False, null=False, max_length=30, verbose_name="組織名")
    description = models.CharField(max_length=200, blank=True, null=True, verbose_name="概要")
    parent = models.ForeignKey(
        "self", related_name='children', blank=True, null=True, on_delete=models.PROTECT, verbose_name="親組織"
    )
    org_type = models.CharField(
        blank=False, null=False, max_length=2, choices=constants.CHOICE_ORG_TYPE, verbose_name="組織類別"
    )

    class Meta:
        db_table = 'eb_organization'

    def __str__(self):
        return self.name


class Member(BaseModel):
    last_name = models.CharField(max_length=10, verbose_name="姓")
    first_name = models.CharField(max_length=10, verbose_name="名")
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
    pay_bank = models.ForeignKey(Bank, blank=True, null=True, on_delete=models.PROTECT, verbose_name="銀行")
    pay_branch = models.ForeignKey(BankBranch, blank=True, null=True, on_delete=models.PROTECT, verbose_name="銀行支店")
    pay_owner = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義")
    pay_owner_kana = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義（カナ）")
    pay_account = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座番号")
    avatar_url = models.CharField(blank=True, null=True, max_length=500, verbose_name="自分の写真")

    class Meta:
        db_table = 'eb_member'

    def __str__(self):
        return '{} {}'.format(self.last_name, self.first_name)
