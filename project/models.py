import re
import datetime
import traceback

from django.core.validators import RegexValidator
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.db import models, connection, transaction
from django.db.models import Max, Sum
from django.utils import timezone

from master.models import ProjectStage, BankAccount, ExpensesCategory
from member.models import Member, Organization
from partner.models import Partner
from utils import constants, common
from utils.errors import CustomException
from utils.models import AbstractCompany, BaseModel, BaseView

logger = common.get_system_logger()


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
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_client'
        default_permissions = ()
        ordering = ['name']
        verbose_name = "取引先"
        verbose_name_plural = '取引先一覧'

    def get_pay_date(self, date=timezone.now().today()):
        """支払い期限日を取得する。

        :param date:
        :return:
        """
        months = int(self.payment_month) if self.payment_month else 1
        pay_month = common.add_months(date, months)
        if self.payment_day == '99' or not self.payment_day:
            return common.get_last_day_by_month(pay_month)
        else:
            pay_day = int(self.payment_day)
            last_day = common.get_last_day_by_month(pay_month)
            if last_day.day < pay_day:
                return last_day
            return datetime.date(pay_month.year, pay_month.month, pay_day)


class ClientMember(BaseModel):
    name = models.CharField(max_length=30, verbose_name="名前")
    email = models.EmailField(blank=True, null=True, verbose_name="メールアドレス")
    phone = models.CharField(max_length=11, blank=True, null=True, verbose_name="電話番号")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, verbose_name="所属会社")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

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
    organization = models.ForeignKey(
        Organization, blank=True, null=True, db_column='department_id', verbose_name="所属部署", on_delete=models.PROTECT,
    )
    status = models.CharField(max_length=1, choices=constants.CHOICE_PROJECT_STATUS, verbose_name="ステータス")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

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

    def get_project_request(self, year, month, client_order):
        """請求番号を取得する。

        :param year: 対象年
        :param month: 対象月
        :param client_order: 注文書
        :return:
        """
        try:
            return self.projectrequest_set.get(year=year, month=month, client_order=client_order)
        except ObjectDoesNotExist:
            # 指定年月の請求番号がない場合、請求番号を発行する。
            next_request_no = self.get_next_request_no(year, month)
            return ProjectRequest(
                project=self,
                client_order=client_order,
                year=year,
                month=month,
                request_no=next_request_no
            )

    @classmethod
    def get_next_request_no(cls, year, month):
        max_request_no = ProjectRequest.objects.filter(year=year, month=month).aggregate(Max('request_no'))
        request_no = max_request_no.get('request_no__max')
        if request_no and re.match(r"^([0-9]{7}|[0-9]{7}-[0-9]{3})$", request_no):
            no = request_no[4:7]
            no = "%03d" % (int(no) + 1,)
            next_request_no = "%s%s%s" % (year[2:], month, no)
        else:
            next_request_no = "%s%s%s" % (year[2:], month, "001")
        return next_request_no

    def get_project_members_by_month(self, year, month):
        """指定年月に案件にアサインしているメンバー

        :param year:
        :param month:
        :return:
        """
        first_day = common.get_first_day_from_ym(year + month)
        last_day = common.get_last_day_by_month(first_day)
        return self.projectmember_set.filter(
            start_date__lte=last_day,
            end_date__gte=first_day,
            is_deleted=False
        ).exclude(
            status='1'  # 提案中を除外
        )


class ProjectMember(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='案件')
    member = models.ForeignKey(Member, on_delete=models.PROTECT, verbose_name="メンバー")
    start_date = models.DateField(blank=False, null=True, verbose_name="開始日")
    end_date = models.DateField(blank=False, null=True, verbose_name="終了日")
    price = models.IntegerField(default=0, verbose_name="単価")
    min_hours = models.DecimalField(max_digits=5, decimal_places=2, default=160, verbose_name="基準時間")
    max_hours = models.DecimalField(max_digits=5, decimal_places=2, default=180, verbose_name="最大時間")
    plus_per_hour = models.IntegerField(default=0, verbose_name="増（円）")
    minus_per_hour = models.IntegerField(default=0, verbose_name="減（円）")
    hourly_pay = models.IntegerField(
        blank=True, null=True, verbose_name="時給", help_text='時給が設定したら、単価などの精算条件が無視される'
    )
    role = models.CharField(max_length=2, default="PG", choices=constants.CHOICE_PROJECT_ROLE, verbose_name="作業区分")
    contract_type = models.CharField(
        max_length=2, blank=True, null=True, choices=constants.CHOICE_CLIENT_CONTRACT_TYPE,
        verbose_name="契約形態"
    )
    stages = models.ManyToManyField(ProjectStage, blank=True, verbose_name="作業工程")
    status = models.CharField(
        max_length=1, null=False, default=1,
        choices=constants.CHOICE_PROJECT_MEMBER_STATUS, verbose_name="ステータス"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_projectmember'
        ordering = ('-end_date',)
        default_permissions = ()
        verbose_name = "案件メンバー"
        verbose_name_plural = '案件メンバー一覧'

    def __str__(self):
        return str(self.member)

    def get_attendance(self, year, month):
        """指定された年月によって、該当するメンバーの勤怠情報を取得する。

        :param year: 対象年
        :param month: 対象月
        :return: MemberAttendanceのインスタンス、または None
        """
        try:
            return self.memberattendance_set.get(year=year, month=month, is_deleted=False)
        except ObjectDoesNotExist:
            raise CustomException(constants.ERROR_NO_ATTENDANCE)

    def get_attendance_dict(self, year, month):
        """指定された年月の出勤情報を取得する。

        :param year: 対象年
        :param month: 対象月
        :return:
        """
        attendance = self.get_attendance(year, month)
        d = dict()
        # 勤務時間
        d['ITEM_WORK_HOURS'] = attendance.total_hours if attendance else ""

        if self.project.is_hourly_pay:
            # 基本金額
            d['ITEM_AMOUNT_BASIC'] = 0
            # 残業時間
            d['ITEM_EXTRA_HOURS'] = 0
            # 率
            d['ITEM_RATE'] = 1
            # 減（円）
            d['ITEM_MINUS_PER_HOUR'] = 0
            # 増（円）
            d['ITEM_PLUS_PER_HOUR'] = 0
            # 基本金額＋残業金額
            d['ITEM_AMOUNT_TOTAL'] = attendance.price if attendance else 0
        else:
            # 基本金額
            d['ITEM_AMOUNT_BASIC'] = self.price if attendance else ""
            # 残業時間
            d['ITEM_EXTRA_HOURS'] = attendance.extra_hours if attendance else ""
            # 率
            d['ITEM_RATE'] = attendance.rate if attendance and attendance.rate else 1
            # 減（円）
            if self.minus_per_hour is None:
                d['ITEM_MINUS_PER_HOUR'] = (self.price / self.min_hours) if attendance else ""
            else:
                d['ITEM_MINUS_PER_HOUR'] = self.minus_per_hour
            # 増（円）
            if self.plus_per_hour is None:
                d['ITEM_PLUS_PER_HOUR'] = (self.price / self.max_hours) if attendance else ""
            else:
                d['ITEM_PLUS_PER_HOUR'] = self.plus_per_hour

            if attendance and attendance.extra_hours > 0:
                d['ITEM_AMOUNT_EXTRA'] = attendance.extra_hours * d['ITEM_PLUS_PER_HOUR']
                d['ITEM_PLUS_PER_HOUR2'] = d['ITEM_PLUS_PER_HOUR']
                d['ITEM_MINUS_PER_HOUR2'] = ""
            elif attendance and attendance.extra_hours < 0:
                d['ITEM_AMOUNT_EXTRA'] = attendance.extra_hours * d['ITEM_MINUS_PER_HOUR']
                d['ITEM_PLUS_PER_HOUR2'] = ""
                d['ITEM_MINUS_PER_HOUR2'] = d['ITEM_MINUS_PER_HOUR']
            else:
                d['ITEM_AMOUNT_EXTRA'] = 0
                d['ITEM_PLUS_PER_HOUR2'] = ""
                d['ITEM_MINUS_PER_HOUR2'] = ""
            # 基本金額＋残業金額
            d['ITEM_AMOUNT_TOTAL'] = attendance.price if attendance else self.price
        # 精算金額
        expense = self.memberexpenses_set.filter(
            year=str(year),
            month="%02d" % int(month),
            is_deleted=False
        ).aggregate(price=Sum('price'))
        d['ITEM_EXPENSES_PRICE'] = expense.get('price') if expense.get('price') else 0
        # 備考
        d['ITEM_COMMENT'] = attendance.comment if attendance and attendance.comment else ""
        d['ITEM_OTHER'] = ""

        return d


class VProject(BaseView):
    name = models.CharField(max_length=50, blank=False, null=False, verbose_name="案件名称")
    client_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="関連会社ＩＤ")
    client_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="関連会社名称")
    business_type = models.CharField(
        max_length=2, blank=False, null=True,
        choices=constants.CHOICE_PROJECT_BUSINESS_TYPE,
        verbose_name="事業分類",
    )
    salesperson_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="営業ＩＤ")
    salesperson_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="営業員")
    member_name = models.CharField(max_length=30, blank=True, null=True, verbose_name="メンバー")
    start_date = models.DateField(blank=True, null=True, verbose_name="開始日")
    end_date = models.DateField(blank=True, null=True, verbose_name="終了日",)
    status = models.IntegerField(choices=constants.CHOICE_PROJECT_STATUS, verbose_name="ステータス")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")

    class Meta:
        managed = False
        db_table = 'v_project'
        default_permissions = ()
        verbose_name = "案件"
        verbose_name_plural = '案件一覧1'


class MemberAttendance(BaseModel):
    project_member = models.ForeignKey(ProjectMember, on_delete=models.PROTECT, verbose_name="メンバー")
    year = models.CharField(max_length=4, verbose_name="対象年")
    month = models.CharField(max_length=2, verbose_name="対象月")
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=1, verbose_name="率")
    salary = models.IntegerField(default=0, editable=False, verbose_name="給料")
    cost = models.IntegerField(default=0, editable=False, verbose_name="コスト", help_text="交通費、残業、保険など含む")
    basic_price = models.IntegerField(default=0, editable=False, verbose_name="単価")
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="合計時間")
    total_hours_bp = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name="ＢＰ作業時間")
    extra_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="残業時間")
    total_days = models.IntegerField(blank=True, null=True, editable=False, verbose_name="勤務日数")
    night_days = models.IntegerField(blank=True, null=True, editable=False, verbose_name="深夜日数")
    advances_paid = models.IntegerField(blank=True, null=True, editable=False, verbose_name="立替金")
    advances_paid_client = models.IntegerField(blank=True, null=True, editable=False, verbose_name="客先立替金")
    traffic_cost = models.IntegerField(
        blank=True, null=True, editable=False, verbose_name="勤務交通費",
        help_text="今月に勤務交通費がない場合、先月のを使用する。"
    )
    allowance = models.IntegerField(
        blank=True, null=True, editable=False, verbose_name="手当",
        help_text="今月に手当がない場合、先月のを使用する。"
    )
    expenses = models.IntegerField(blank=True, null=True, editable=False, verbose_name="経費")
    min_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False, verbose_name="基準時間")
    max_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False, verbose_name="最大時間")
    plus_per_hour = models.IntegerField(default=0, editable=False, verbose_name="増（円）")
    minus_per_hour = models.IntegerField(default=0, editable=False, verbose_name="減（円）")
    price = models.IntegerField(default=0, verbose_name="価格")
    expect_price = models.IntegerField(blank=True, null=True, verbose_name="請求金額")
    comment = models.CharField(blank=True, null=True, max_length=50, verbose_name="備考")
    # 経費（原価ではない、営業コストとする）
    expenses_conference = models.IntegerField(default=0, verbose_name="会議費")
    expenses_entertainment = models.IntegerField(default=0, verbose_name="交際費")
    expenses_travel = models.IntegerField(default=0, verbose_name="旅費交通費")
    expenses_communication = models.IntegerField(default=0, verbose_name="通信費")
    expenses_tax_dues = models.IntegerField(default=0, verbose_name="租税公課")
    expenses_expendables = models.IntegerField(default=0, verbose_name="消耗品")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_memberattendance'
        ordering = ('project_member', 'year', 'month')
        unique_together = ('project_member', 'year', 'month')
        verbose_name = "勤務時間"
        verbose_name_plural = "勤務時間一覧"


class MemberExpenses(BaseModel):
    project_member = models.ForeignKey(ProjectMember, on_delete=models.PROTECT, verbose_name="要員")
    year = models.CharField(max_length=4, validators=(RegexValidator(regex='^20[0-9]{2}$'),), verbose_name="対象年")
    month = models.CharField(max_length=2, choices=constants.CHOICE_MONTH_LIST, verbose_name="対象月")
    category = models.ForeignKey(ExpensesCategory, on_delete=models.PROTECT, verbose_name="分類")
    price = models.IntegerField(default=0, verbose_name="金額")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_memberexpenses'
        default_permissions = ()
        verbose_name = "取引先精算"
        verbose_name_plural = "取引先精算一覧"


class ClientOrder(BaseModel):
    projects = models.ManyToManyField(Project, verbose_name="案件")
    name = models.CharField(max_length=50, verbose_name="注文書名称")
    start_date = models.DateField(verbose_name="開始日")
    end_date = models.DateField(verbose_name="終了日")
    order_no = models.CharField(max_length=20, verbose_name="注文番号")
    order_date = models.DateField(blank=False, null=True, verbose_name="注文日")
    contract_type = models.CharField(
        max_length=2, blank=False, null=True,
        choices=constants.CHOICE_CLIENT_CONTRACT_TYPE, verbose_name="契約形態"
    )
    bank_account = models.ForeignKey(
        BankAccount, blank=False, null=True, db_column='bank_info_id', on_delete=models.PROTECT, verbose_name="振込先口座"
    )
    # order_file = models.FileField(blank=True, null=True, upload_to=get_client_order_path, verbose_name="注文書")
    # member_comma_list = models.CharField(max_length=255, blank=True, null=True, editable=False,
    #                                      verbose_name="メンバー主キーのリスト",
    #                                      validators=[validate_comma_separated_integer_list])
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_clientorder'
        default_permissions = ()
        verbose_name = "案件注文書"
        verbose_name_plural = "案件注文書一覧"

    def __str__(self):
        return self.name


class ProjectRequest(BaseModel):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name="案件")
    client_order = models.ForeignKey(ClientOrder, blank=True, null=True, on_delete=models.PROTECT, verbose_name="注文書")
    year = models.CharField(max_length=4, validators=(RegexValidator(regex='^20[0-9]{2}$'),), verbose_name="対象年")
    month = models.CharField(max_length=2, choices=constants.CHOICE_MONTH_LIST, verbose_name="対象月")
    request_no = models.CharField(max_length=7, unique=True, verbose_name="請求番号")
    request_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="請求名称")
    cost = models.IntegerField(default=0, verbose_name="コスト")
    amount = models.IntegerField(default=0, verbose_name="請求金額（税込）")
    turnover_amount = models.IntegerField(default=0, verbose_name="売上金額（基本単価＋残業料）（税抜き）")
    tax_amount = models.IntegerField(default=0, verbose_name="税金")
    expenses_amount = models.IntegerField(default=0, verbose_name="精算金額")
    filename = models.CharField(max_length=255, blank=True, null=True, verbose_name="請求書ファイル名")
    created_user = models.ForeignKey(
        User, related_name='created_requests', null=True, on_delete=models.PROTECT,
        editable=False, verbose_name="作成者"
    )
    updated_user = models.ForeignKey(
        User, related_name='updated_requests', null=True, on_delete=models.PROTECT,
        editable=False, verbose_name="更新者"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")

    class Meta:
        managed = False
        db_table = 'eb_projectrequest'
        default_permissions = ()
        ordering = ('-request_no',)
        unique_together = ('project', 'client_order', 'year', 'month')
        verbose_name = "案件請求情報"
        verbose_name_plural = "案件請求情報一覧"

    def __str__(self):
        return self.request_no

    @transaction.atomic
    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None, other_data=None):
        super(ProjectRequest, self).save(force_insert, force_update, using, update_fields)
        # 請求書作成時、請求に関する全ての情報を履歴として保存する。
        if other_data:
            data = other_data
            # 既存のデータを全部消す。
            if hasattr(self, "projectrequestheading"):
                self.projectrequestheading.delete()
            self.projectrequestdetail_set.all().delete()
            heading = ProjectRequestHeading(
                project_request=self,
                is_lump=self.project.is_lump,
                lump_amount=self.project.lump_amount,
                lump_comment=self.project.lump_comment,
                is_hourly_pay=self.project.is_hourly_pay,
                client=self.project.client,
                client_post_code=data['heading']['CLIENT_POST_CODE'],
                client_address=data['heading']['CLIENT_ADDRESS'],
                client_tel=data['heading']['CLIENT_TEL'],
                client_name=data['heading']['CLIENT_COMPANY_NAME'],
                tax_rate=self.project.client.tax_rate,
                decimal_type=self.project.client.decimal_type,
                work_period_start=data['heading']['WORK_PERIOD_START'],
                work_period_end=data['heading']['WORK_PERIOD_END'],
                remit_date=data['heading']['REMIT_DATE_PURE'],
                publish_date=data['heading']['PUBLISH_DATE_PURE'],
                company_post_code=data['heading']['POST_CODE'],
                company_address=data['heading']['ADDRESS'],
                company_name=data['heading']['COMPANY_NAME'],
                company_tel=data['heading']['TEL'],
                company_master=data['heading']['MASTER'],
                bank_account=data['heading']['BANK_ACCOUNT'],
                bank_name=data['heading']['BANK_NAME'],
                branch_no=data['heading']['BRANCH_NO'],
                branch_name=data['heading']['BRANCH_NAME'],
                account_type=data['heading']['ACCOUNT_TYPE_PURE'],
                account_number=data['heading']['ACCOUNT_NUMBER'],
                account_holder=data['heading']['BANK_ACCOUNT_HOLDER']
            )
            heading.save()
            for i, item in enumerate(data['MEMBERS'], start=1):
                project_member = item["EXTRA_PROJECT_MEMBER"]
                total_hours = item['ITEM_WORK_HOURS'] if item['ITEM_WORK_HOURS'] else 0
                expenses_price = item['ITEM_EXPENSES_PRICE']
                try:
                    member_attendance = MemberAttendance.objects.get(
                        project_member=project_member, year=self.year, month=self.month
                    )
                    with connection.cursor() as cursor:
                        cursor.callproc('sp_project_member_cost', [
                            project_member.member.pk,
                            project_member.pk,
                            self.year,
                            self.month,
                            len(common.get_business_days(self.year, self.month)),
                            member_attendance.total_hours_bp or member_attendance.total_hours,
                            member_attendance.allowance or 0,
                            member_attendance.night_days or 0,
                            member_attendance.traffic_cost or 0,
                            expenses_price,
                        ])
                        dict_cost = common.dictfetchall(cursor)[0]
                except Exception as ex:
                    logger.error(ex)
                    logger.error(traceback.format_exc())
                    dict_cost = dict()
                detail = ProjectRequestDetail(
                    project_request=self,
                    project_member=project_member,
                    year=self.year,
                    month=self.month,
                    organization_id=52,  # TODO: 社員の部署取得
                    member_type='1',  # TODO: 社員の契約形態
                    # salesperson_id=16,  # TODO: 社員の営業員取得
                    partner_id=1,  # TODO: 協力会社取得,
                    salary=dict_cost.get('salary', 0) or 0,
                    cost=dict_cost.get('cost', 0) or 0,
                    no=str(i),
                    hourly_pay=project_member.hourly_pay if project_member.hourly_pay else 0,
                    basic_price=project_member.price,
                    min_hours=project_member.min_hours,
                    max_hours=project_member.max_hours,
                    total_hours=total_hours,
                    extra_hours=item['ITEM_EXTRA_HOURS'] if item['ITEM_EXTRA_HOURS'] else 0,
                    rate=item['ITEM_RATE'],
                    plus_per_hour=project_member.plus_per_hour,
                    minus_per_hour=project_member.minus_per_hour,
                    total_price=item['ITEM_AMOUNT_TOTAL'],
                    expenses_price=expenses_price,
                    comment=item['ITEM_COMMENT']
                )
                detail.save()


class ProjectRequestHeading(BaseModel):
    project_request = models.OneToOneField(ProjectRequest, on_delete=models.PROTECT, verbose_name="請求書")
    is_lump = models.BooleanField(default=False, verbose_name="一括フラグ")
    lump_amount = models.BigIntegerField(default=0, blank=True, null=True, verbose_name="一括金額")
    lump_comment = models.CharField(blank=True, null=True, max_length=200, verbose_name="一括の備考")
    is_hourly_pay = models.BooleanField(default=False, verbose_name="時給")
    client = models.ForeignKey(Client, null=True, on_delete=models.PROTECT, verbose_name="関連会社")
    client_post_code = models.CharField(blank=True, null=True, max_length=8, verbose_name="お客様郵便番号")
    client_address = models.CharField(blank=True, null=True, max_length=200, verbose_name="お客様住所１")
    client_tel = models.CharField(blank=True, null=True, max_length=15, verbose_name="お客様電話番号")
    client_name = models.CharField(blank=True, null=True, max_length=30, verbose_name="お客様会社名")
    tax_rate = models.DecimalField(blank=True, null=True, max_digits=3, decimal_places=2, verbose_name="税率")
    decimal_type = models.CharField(
        blank=True, null=True, max_length=1, choices=constants.CHOICE_DECIMAL_TYPE,
        verbose_name="小数の処理区分"
    )
    work_period_start = models.DateField(blank=True, null=True, verbose_name="作業期間＿開始")
    work_period_end = models.DateField(blank=True, null=True, verbose_name="作業期間＿終了")
    remit_date = models.DateField(blank=True, null=True, verbose_name="お支払い期限")
    publish_date = models.DateField(blank=True, null=True, verbose_name="発行日")
    company_post_code = models.CharField(blank=True, null=True, max_length=8, verbose_name="本社郵便番号")
    company_address = models.CharField(blank=True, null=True, max_length=200, verbose_name="本社住所")
    company_name = models.CharField(blank=True, null=True, max_length=30, verbose_name="会社名")
    company_tel = models.CharField(blank=True, null=True, max_length=15, verbose_name="お客様電話番号")
    company_master = models.CharField(blank=True, null=True, max_length=30, verbose_name="代表取締役")
    bank_account = models.ForeignKey(
        BankAccount, blank=True, null=True, db_column='bank_id', on_delete=models.PROTECT, verbose_name="口座"
    )
    bank_name = models.CharField(blank=True, null=True, max_length=20, verbose_name="銀行名称")
    branch_no = models.CharField(blank=True, null=True, max_length=3, verbose_name="支店番号")
    branch_name = models.CharField(blank=True, null=True, max_length=20, verbose_name="支店名称")
    account_type = models.CharField(
        blank=True, null=True, max_length=1, choices=constants.CHOICE_BANK_ACCOUNT_TYPE,
        verbose_name="預金種類"
    )
    account_number = models.CharField(blank=True, null=True, max_length=7, verbose_name="口座番号")
    account_holder = models.CharField(blank=True, null=True, max_length=20, verbose_name="口座名義")

    class Meta:
        managed = False
        db_table = 'eb_projectrequestheading'
        default_permissions = ()
        verbose_name = "案件請求見出し"
        verbose_name_plural = "案件請求見出し一覧"


class ProjectRequestDetail(BaseModel):
    project_request = models.ForeignKey(ProjectRequest, on_delete=models.PROTECT, verbose_name="請求書")
    project_member = models.ForeignKey(ProjectMember, on_delete=models.PROTECT, verbose_name="メンバー")
    year = models.CharField(max_length=4, blank=True, null=True, verbose_name="対象年")
    month = models.CharField(max_length=2, blank=True, null=True, verbose_name="対象月")
    organization = models.ForeignKey(
        Organization, db_column='member_section_id', on_delete=models.PROTECT, verbose_name="部署"
    )
    member_type = models.CharField(max_length=1, choices=constants.CHOICE_MEMBER_TYPE, verbose_name="社員区分")
    # salesperson = models.ForeignKey(Salesperson, blank=True, null=True, on_delete=models.PROTECT, verbose_name="営業員")
    partner = models.ForeignKey(
        Partner, blank=True, null=True, db_column='subcontractor_id', on_delete=models.PROTECT,
        verbose_name="協力会社"
    )
    salary = models.IntegerField(default=0, verbose_name="給料")
    cost = models.IntegerField(default=0, verbose_name="コスト")
    no = models.IntegerField(verbose_name="番号")
    hourly_pay = models.IntegerField(default=0, verbose_name="時給")
    basic_price = models.IntegerField(default=0, verbose_name="単価")
    min_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="基準時間")
    max_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="最大時間")
    total_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="合計時間")
    extra_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0, verbose_name="残業時間")
    rate = models.DecimalField(max_digits=3, decimal_places=2, default=1, verbose_name="率")
    plus_per_hour = models.IntegerField(default=0, editable=False, verbose_name="増（円）")
    minus_per_hour = models.IntegerField(default=0, editable=False, verbose_name="減（円）")
    total_price = models.IntegerField(default=0, verbose_name="売上（基本単価＋残業料）（税抜き）")
    expenses_price = models.IntegerField(default=0, verbose_name="精算金額")
    expect_price = models.IntegerField(blank=True, null=True, verbose_name="請求金額")
    comment = models.CharField(max_length=50, blank=True, null=True, verbose_name="備考")

    class Meta:
        managed = False
        db_table = 'eb_projectrequestdetail'
        default_permissions = ()
        unique_together = ('project_request', 'no')
        verbose_name = "案件請求明細"
        verbose_name_plural = "案件請求明細一覧"
