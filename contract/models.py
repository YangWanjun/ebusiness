from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from master.models import Company
from utils import constants
from utils.models import BaseView, BaseModel


# Create your models here.
class VMember(BaseView):
    code = models.CharField(max_length=30, unique=True, verbose_name="コード")
    name = models.CharField(max_length=30, verbose_name='名前')
    gender = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_GENDER, verbose_name="性別"
    )
    birthday = models.DateField(blank=True, null=True, verbose_name="生年月日")
    join_date = models.DateField(blank=True, null=True, verbose_name="入社年月日")
    contract_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="契約ＩＤ")
    contract_no = models.CharField(blank=True, null=True, max_length=20, verbose_name="契約番号")
    member_type = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_MEMBER_TYPE, verbose_name="雇用形態"
    )
    employment_date = models.DateField(blank=True, null=True, verbose_name="雇用日")
    end_date = models.DateField(blank=True, null=True, verbose_name="雇用終了日")
    has_insurance = models.BooleanField(default=False, verbose_name="保険加入")
    is_retired = models.BooleanField(default=False, verbose_name="退職")

    class Meta:
        managed = False
        db_table = 'v_contract_members'
        default_permissions = ()
        verbose_name = "社員"
        verbose_name_plural = "社員一覧"


class Contract(BaseModel):
    # 会社情報
    company_content_type = models.ForeignKey(
        ContentType, on_delete=models.PROTECT, related_name='company_contract_set', verbose_name="契約会社"
    )
    company_object_id = models.PositiveIntegerField(verbose_name="契約会社ID")
    company_content_object = GenericForeignKey('company_content_type', 'company_object_id')
    # 契約対象（社員、案件）
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    # 契約共通情報
    contract_no = models.CharField(max_length=20, verbose_name="契約番号")
    contract_date = models.DateField(verbose_name="契約日")
    start_date = models.DateField(verbose_name="契約開始日")
    end_date = models.DateField(default='9999-12-31', verbose_name="契約終了日")
    is_auto_update = models.BooleanField(default=True, verbose_name="自動更新")
    parent = models.ForeignKey('self', blank=True, null=True, related_name='children', on_delete=models.PROTECT)
    # 社員契約に関する情報
    member_type = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_MEMBER_TYPE, verbose_name="雇用形態",
    )
    is_loan = models.BooleanField(default=False, verbose_name="出向")
    insurance = models.CharField(
        max_length=1, blank=True, null=True, default='0',
        choices=constants.CHOICE_INSURANCE,
        verbose_name="社会保険加入有無",
        help_text="0:加入しない、1:加入する"
    )
    calculate_type = models.CharField(
        max_length=2, blank=True, null=True, choices=constants.CHOICE_CALCULATE_TYPE, verbose_name="時間計算種類"
    )

    class Meta:
        managed = False
        db_table = 'eb_contract_new'
        default_permissions = ()
        verbose_name = "契約"
        verbose_name_plural = "契約一覧"


class ContractComment(BaseModel):
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, verbose_name="契約情報")
    code = models.CharField(max_length=5, choices=constants.CHOICE_CONTRACT_COMMENT, verbose_name="コメントコード")
    name = models.CharField(max_length=50, verbose_name="コメント名称")
    content = models.CharField(max_length=2000, verbose_name="内容")

    class Meta:
        managed = False
        db_table = 'eb_contract_comment'
        default_permissions = ()
        verbose_name = "契約コメント"
        verbose_name_plural = "契約コメント一覧"


class ContractAllowance(BaseModel):
    contract = models.ForeignKey(Contract, on_delete=models.PROTECT, verbose_name="契約情報")
    code = models.CharField(max_length=5, choices=constants.CHOICE_CONTRACT_ALLOWANCE, verbose_name="手当コード")
    name = models.CharField(max_length=50, verbose_name="手当名称")
    amount = models.PositiveIntegerField(verbose_name="金額")
    unit = models.CharField(max_length=2, default='01', choices=constants.CHOICE_ALLOWANCE_UNIT, verbose_name="単位")
    comment = models.CharField(max_length=255, verbose_name="コメント")

    class Meta:
        managed = False
        db_table = 'eb_contract_allowance'
        default_permissions = ()
        verbose_name = "契約手当"
        verbose_name_plural = "契約手当一覧"
