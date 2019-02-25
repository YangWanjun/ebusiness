from django.db import models

from utils import constants
from utils.models import AbstractCompany, BaseModel


# Create your models here.
class Client(AbstractCompany):
    kana = models.CharField(max_length=30, blank=True, null=True, db_column='japanese_spell', verbose_name="フリカナ")
    payment_month = models.CharField(
        max_length=1, blank=True, null=True, default='1',
        choices=constants.CHOICE_PAYMENT_MONTH, verbose_name="支払いサイト"
    )
    payment_day = models.CharField(
        max_length=2, blank=True, null=True, default='99',
        choices=constants.CHOICE_PAYMENT_DAY, verbose_name="支払日"
    )
    tax_rate = models.DecimalField(
        default=0.08, max_digits=3, decimal_places=2, choices=constants.CHOICE_TAX_RATE,
        verbose_name="税率"
    )
    decimal_type = models.CharField(
        max_length=1, default='0', choices=constants.CHOICE_DECIMAL_TYPE,
        verbose_name="小数の処理区分"
    )

    class Meta:
        managed = False
        db_table = 'eb_client'
        default_permissions = ()
        ordering = ['name']
        verbose_name = "取引先"
        verbose_name_plural = '取引先一覧'


class Project(BaseModel):
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name="案件名称")
    description = models.TextField(blank=True, null=True, verbose_name="案件概要")
    business_type = models.CharField(
        max_length=2, blank=False, null=True,
        choices=constants.CHOICE_PROJECT_BUSINESS_TYPE,
        verbose_name="事業分類",
    )
    start_date = models.DateField(blank=True, null=True, verbose_name="開始日")
    end_date = models.DateField(blank=True, null=True, verbose_name="終了日",)
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="作業場所")
    nearest_station = models.CharField(max_length=15, blank=False, null=True, verbose_name="最寄駅",)
    status = models.IntegerField(choices=constants.CHOICE_PROJECT_STATUS, verbose_name="ステータス")
    attendance_type = models.CharField(
        max_length=1, default='1', choices=constants.CHOICE_ATTENDANCE_TYPE, verbose_name="出勤の計算区分"
    )
    min_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=160, verbose_name="基準時間",
        help_text="该项目仅仅是作为项目中各人员时间的默认设置，计算时不会使用该值。"
    )
    max_hours = models.DecimalField(
        max_digits=5, decimal_places=2, default=180, verbose_name="最大時間",
        help_text="该项目仅仅是作为项目中各人员时间的默认设置，计算时不会使用该值。"
    )
    is_lump = models.BooleanField(default=False, verbose_name="一括フラグ")
    lump_amount = models.BigIntegerField(default=0, blank=True, null=True, verbose_name="一括金額")
    lump_comment = models.CharField(
        max_length=200, blank=True, null=True, verbose_name="一括の備考", help_text="该项目会作为请求书中備考栏中的值。"
    )
    is_hourly_pay = models.BooleanField(
        default=False, verbose_name="時給",
        help_text="选中后将会无视人员的单价与增减等信息，计算请求时会将总时间乘以时薪。"
    )
    is_reserve = models.BooleanField(
        default=False, verbose_name="待機案件フラグ",
        help_text="バーチャル案件です、コストなどを算出ために非稼働メンバーをこの案件にアサインすればいい。"
    )
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT, verbose_name="関連会社")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")

    class Meta:
        managed = False
        db_table = 'eb_project'
        ordering = ['name']
        unique_together = ('name', 'client')
        default_permissions = ()
        verbose_name = "案件"
        verbose_name_plural = '案件一覧1'

    def __str__(self):
        return self.name
