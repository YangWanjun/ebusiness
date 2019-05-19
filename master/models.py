from django.core.validators import RegexValidator
from django.db import models

from utils import constants
from utils.models import BaseModel, AbstractCompany


class Company(AbstractCompany):

    class Meta:
        db_table = 'mst_company'
        verbose_name = verbose_name_plural = "自社情報"


class Bank(BaseModel):
    code = models.CharField(
        max_length=4, primary_key=True, validators=(RegexValidator(regex=r'[0-9]{4}'),), verbose_name="金融機関コード"
    )
    name = models.CharField(max_length=30, verbose_name="金融機関名称")
    kana = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="金融機関カナ",
        help_text="半角カナ文字及び英数字等、左詰め残りスペースとする。"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bank'
        ordering = ['code']
        default_permissions = ()
        verbose_name = "金融機関"
        verbose_name_plural = "金融機関一覧"

    def __str__(self):
        return self.name


# class BankBranch(BaseModel):
#     bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="銀行")
#     branch_no = models.CharField(max_length=3, validators=(RegexValidator(regex=r'[0-9]{3}'),), verbose_name="支店番号")
#     branch_name = models.CharField(max_length=20, verbose_name="支店名称")
#     branch_kana = models.CharField(
#         max_length=40, blank=True, null=True, verbose_name="支店カナ",
#         help_text="半角カナ文字及び英数字等、左詰め残りスペースとする。",
#     )
#     address = models.CharField(max_length=200, blank=True, null=True, verbose_name="所在地")
#     tel = models.CharField(
#         max_length=15, blank=True, null=True, verbose_name="電話番号",
#         validators=(RegexValidator(regex=constants.REG_TEL),)
#     )
#
#     class Meta:
#         db_table = 'mst_bank_branch'
#         ordering = ['bank', 'branch_no']
#         verbose_name = "銀行支店"
#         verbose_name_plural = "銀行支店一覧"
#
#     def __str__(self):
#         return self.branch_name


class BankAccount(BaseModel):
    bank = models.ForeignKey(Bank, verbose_name="銀行", on_delete=models.PROTECT)
    branch_no = models.CharField(max_length=3, validators=(RegexValidator(regex=r'[0-9]{3}'),), verbose_name="支店番号")
    branch_name = models.CharField(max_length=20, verbose_name="支店名称")
    branch_kana = models.CharField(max_length=40, blank=True, null=True, verbose_name="支店カナ",)
    account_type = models.CharField(max_length=1, choices=constants.CHOICE_BANK_ACCOUNT_TYPE, verbose_name="預金種類")
    account_number = models.CharField(
        max_length=7, validators=(RegexValidator(regex=r'[0-9]{7}'),), verbose_name="口座番号"
    )
    account_holder = models.CharField(blank=True, null=True, max_length=30, verbose_name="口座名義")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bankinfo'
        default_permissions = ()
        verbose_name = "銀行口座"
        verbose_name_plural = "銀行口座一覧"

    def __str__(self):
        return self.account_number


class ProjectStage(BaseModel):
    name = models.CharField(max_length=15, unique=True, verbose_name="作業工程名称")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'mst_project_stage'
        default_permissions = ()
        verbose_name = "作業工程"
        verbose_name_plural = '作業工程一覧'

    def __str__(self):
        return self.name
