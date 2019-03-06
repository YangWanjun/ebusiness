from django.db import models

from master.models import ProjectStage
from member.models import Member
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


class ClientMember(BaseModel):
    name = models.CharField(max_length=30, verbose_name="名前")
    email = models.EmailField(blank=True, null=True, verbose_name="メールアドレス")
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="電話番号")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="所属会社")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")

    class Meta:
        managed = False
        db_table = 'eb_clientmember'
        default_permissions = ()
        ordering = ['name']
        verbose_name = "お客様"
        verbose_name_plural = 'お客様一覧'

    def __str__(self):
        return self.name


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
    address1 = models.CharField(max_length=255, blank=True, null=True, db_column='address', verbose_name="作業場所")
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
    manager = models.ForeignKey(
        ClientMember, blank=False, null=True, db_column='boss_id', on_delete=models.PROTECT,
        related_name="manager_set", verbose_name="案件責任者"
    )
    contact = models.ForeignKey(
        ClientMember, blank=True, null=True, db_column='middleman_id', on_delete=models.PROTECT,
        related_name="contact_set", verbose_name="案件連絡者"
    )
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


class ProjectMember(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='案件')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, verbose_name="名前")
    start_date = models.DateField(blank=False, null=True, verbose_name="開始日")
    end_date = models.DateField(blank=False, null=True, verbose_name="終了日")
    price = models.IntegerField(default=0, verbose_name="単価")
    min_hours = models.DecimalField(max_digits=5, decimal_places=2, default=160, verbose_name="基準時間")
    max_hours = models.DecimalField(max_digits=5, decimal_places=2, default=180, verbose_name="最大時間")
    plus_per_hour = models.IntegerField(default=0, verbose_name="増（円）")
    minus_per_hour = models.IntegerField(default=0, verbose_name="減（円）")
    hourly_pay = models.IntegerField(blank=True, null=True, verbose_name="時給")
    status = models.CharField(
        max_length=1, null=False, default=1,
        choices=constants.CHOICE_PROJECT_MEMBER_STATUS, verbose_name="ステータス"
    )
    role = models.CharField(max_length=2, default="PG", choices=constants.CHOICE_PROJECT_ROLE, verbose_name="作業区分")
    contract_type = models.CharField(
        max_length=2, blank=True, null=True, choices=constants.CHOICE_CLIENT_CONTRACT_TYPE,
        verbose_name="契約形態"
    )
    stages = models.ManyToManyField(ProjectStage, blank=True, verbose_name="作業工程")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")

    class Meta:
        managed = False
        db_table = 'eb_projectmember'
        default_permissions = ()
        verbose_name = "案件メンバー"
        verbose_name_plural = '案件メンバー一覧'

    def __str__(self):
        return str(self.member)
