from django.db import models

from utils import constants
from utils.models import BaseView


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
