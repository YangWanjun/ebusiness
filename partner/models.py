from django.core.validators import RegexValidator
from django.db import models

from master.models import Bank
from utils import constants
from utils.models import AbstractCompany, AbstractMember, BaseModel, AbstractBankAccount


class Partner(AbstractCompany):
    kana = models.CharField(max_length=30, blank=True, null=True, db_column='japanese_spell', verbose_name="フリカナ")
    employee_count = models.IntegerField(blank=True, null=True, verbose_name="従業員数")
    sales_amount = models.BigIntegerField(blank=True, null=True, db_column='sale_amount', verbose_name="売上高")
    payment_month = models.CharField(
        blank=True, null=True, max_length=1, default='1',
        choices=constants.CHOICE_PAYMENT_MONTH, verbose_name="支払いサイト"
    )
    payment_day = models.CharField(
        blank=True, null=True, max_length=2, choices=constants.CHOICE_PAYMENT_DAY,
        default='99', verbose_name="支払日"
    )
    middleman = models.CharField(blank=True, null=True, max_length=30, verbose_name="連絡窓口担当者")
    comment = models.CharField(max_length=250, blank=True, null=True, verbose_name="備考")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_subcontractor'
        default_permissions = ()
        verbose_name = "協力会社"
        verbose_name_plural = '協力会社一覧'


class PartnerEmployee(BaseModel):
    company = models.ForeignKey(Partner, db_column='subcontractor_id', on_delete=models.PROTECT, verbose_name='協力会社')
    name = models.CharField(max_length=30, verbose_name="名前")
    email = models.EmailField(blank=False, null=True, verbose_name="メールアドレス")
    phone = models.CharField(
        blank=True, null=True, max_length=11,
        validators=(RegexValidator(regex=constants.REG_TEL),),
        verbose_name="電話番号"
    )
    member_type = models.CharField(max_length=2, choices=constants.CHOICE_PARTNER_POSITION, verbose_name="役割担当")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_subcontractormember'
        default_permissions = ()
        verbose_name = "ＢＰ社員"
        verbose_name_plural = 'ＢＰ社員一覧'


class PartnerPayNotifyRecipient(BaseModel):
    company = models.ForeignKey(
        Partner, db_column='subcontractor_id', on_delete=models.PROTECT, verbose_name="所属会社",
    )
    member = models.ForeignKey(
        PartnerEmployee, db_column='subcontractor_member_id', on_delete=models.PROTECT, verbose_name="所属会社社員",
    )
    is_cc = models.BooleanField(default=False, verbose_name="ＣＣに入れて送信")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_subcontractorrequestrecipient'
        default_permissions = ()
        verbose_name = "支払通知書の宛先"
        verbose_name_plural = "支払通知書の宛先一覧"


class PartnerBankAccount(AbstractBankAccount):
    company = models.ForeignKey(
        Partner, db_column='subcontractor_id', on_delete=models.PROTECT, verbose_name="所属会社",
    )
    bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="銀行")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_subcontractorbankinfo'
        default_permissions = ()
        verbose_name = "協力会社銀行口座"
        verbose_name_plural = "協力会社銀行口座一覧"

