import datetime

from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User

from master.models import Bank
from member.models import Member
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


class BpContract(BaseModel):
    company = models.ForeignKey(Partner, on_delete=models.PROTECT, verbose_name="雇用会社")
    member = models.ForeignKey(Member, on_delete=models.PROTECT, verbose_name="社員")
    contract_type = models.CharField(
        max_length=2, default='02', choices=constants.CHOICE_BP_CONTRACT_TYPE, verbose_name="契約形態"
    )
    start_date = models.DateField(verbose_name="雇用開始日")
    end_date = models.DateField(default=datetime.date.max, verbose_name="雇用終了日")
    is_hourly_pay = models.BooleanField(default=False, verbose_name="時給")
    is_fixed_cost = models.BooleanField(default=False, verbose_name="固定")
    is_show_formula = models.BooleanField(
        default=True, verbose_name="計算式",
        help_text="注文書に超過単価と不足単価の計算式を表示するか"
    )
    allowance_base = models.IntegerField(verbose_name="基本給")
    allowance_base_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="基本給メモ")
    allowance_time_min = models.DecimalField(
        default=160, max_digits=5, decimal_places=2, verbose_name="時間下限",
        help_text="足りないなら欠勤となる"
    )
    allowance_time_max = models.DecimalField(
        default=200, max_digits=5, decimal_places=2, verbose_name="時間上限",
        help_text="超えたら残業となる"
    )
    allowance_time_memo = models.CharField(
        max_length=255, blank=True, null=True,
        default="※基準時間：160～200/月", verbose_name="基準時間メモ"
    )
    calculate_type = models.CharField(
        default='99', max_length=2, choices=constants.CHOICE_CALCULATE_TYPE,
        verbose_name="計算種類"
    )
    business_days = models.IntegerField(blank=True, null=True, verbose_name="営業日数")
    calculate_time_min = models.DecimalField(
        blank=True, null=True, default=160, max_digits=5, decimal_places=2,
        verbose_name="計算用下限", help_text="欠勤手当を算出ために使われます。"
    )
    calculate_time_max = models.DecimalField(
        blank=True, null=True, default=200, max_digits=5, decimal_places=2,
        verbose_name="計算用上限", help_text="残業手当を算出ために使われます。"
    )
    allowance_overtime = models.IntegerField(default=0, verbose_name="残業手当")
    allowance_overtime_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="残業手当メモ")
    allowance_absenteeism = models.IntegerField(default=0, verbose_name="欠勤手当")
    allowance_absenteeism_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="欠勤手当メモ")
    allowance_other = models.IntegerField(default=0, verbose_name="その他手当")
    allowance_other_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="その他手当メモ")
    status = models.CharField(
        max_length=2, default='01', choices=constants.CHOICE_CONTRACT_STATUS,
        verbose_name="契約状態"
    )
    comment = models.TextField(blank=True, null=True, verbose_name="備考")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bp_contract'
        default_permissions = ()
        ordering = ['company', 'member', '-start_date']
        verbose_name = "ＢＰ契約"
        verbose_name_plural = "ＢＰ契約一覧"


class BpMemberOrder(BaseModel):
    project_member = models.ForeignKey('project.ProjectMember', on_delete=models.PROTECT, verbose_name="案件メンバー")
    member = models.ForeignKey(Partner, db_column='subcontractor_id', on_delete=models.PROTECT, verbose_name="協力会社")
    order_no = models.CharField(max_length=14, unique=True, verbose_name="注文番号")
    year = models.CharField(max_length=4, validators=(RegexValidator(regex='^20[0-9]{2}$'),), verbose_name="開始年")
    month = models.CharField(max_length=2, choices=constants.CHOICE_MONTH_LIST, verbose_name="開始月")
    end_year = models.CharField(max_length=4, validators=(RegexValidator(regex='^20[0-9]{2}$'),), verbose_name="終了年")
    end_month = models.CharField(max_length=2, choices=constants.CHOICE_MONTH_LIST, verbose_name="終了月")
    filename = models.CharField(max_length=255, blank=True, null=True, verbose_name="注文書ファイル名")
    filename_request = models.CharField(max_length=255, blank=True, null=True, verbose_name="注文請書")
    is_sent = models.BooleanField(default=False, verbose_name="送信")
    created_user = models.ForeignKey(
        User, related_name='created_bp_orders', null=True, on_delete=models.PROTECT,
        editable=False, verbose_name="作成者"
    )
    updated_user = models.ForeignKey(
        User, related_name='updated_bp_orders', null=True, on_delete=models.PROTECT,
        editable=False, verbose_name="更新者"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bpmemberorder'
        default_permissions = ()
        unique_together = ('project_member', 'year', 'month')
        verbose_name = "ＢＰ註文書"
        verbose_name_plural = "ＢＰ註文書一覧"


class BpMemberOrderHeading(BaseModel):
    order = models.OneToOneField(BpMemberOrder, db_column='bp_order_id', on_delete=models.PROTECT, verbose_name="ＢＰ注文書")
    publish_date = models.CharField(max_length=200, verbose_name="発行年月日")
    partner_name = models.CharField(
        max_length=50, blank=True, null=True, db_column='subcontractor_name', verbose_name="下請け会社名"
    )
    partner_post_code = models.CharField(
        max_length=8, blank=True, null=True, db_column='subcontractor_post_code', verbose_name="協力会社郵便番号"
    )
    partner_address1 = models.CharField(
        max_length=200, blank=True, null=True, db_column='subcontractor_address1', verbose_name="協力会社住所１"
    )
    partner_address2 = models.CharField(
        max_length=200, blank=True, null=True, db_column='subcontractor_address2', verbose_name="協力会社住所２"
    )
    partner_tel = models.CharField(
        max_length=15, blank=True, null=True, db_column='subcontractor_tel', verbose_name="協力会社電話番号"
    )
    partner_fax = models.CharField(
        max_length=15, blank=True, null=True, db_column='subcontractor_fax', verbose_name="協力会社ファックス"
    )
    company_address1 = models.CharField(blank=True, null=True, max_length=200, verbose_name="本社住所１")
    company_address2 = models.CharField(blank=True, null=True, max_length=200, verbose_name="本社住所２")
    company_name = models.CharField(blank=True, null=True, max_length=30, verbose_name="会社名")
    company_tel = models.CharField(blank=True, null=True, max_length=15, verbose_name="お客様電話番号")
    project_name = models.CharField(blank=True, null=True, max_length=50, verbose_name="業務名称")
    start_date = models.CharField(blank=True, null=True, max_length=20, verbose_name="作業開始日")
    end_date = models.CharField(blank=True, null=True, max_length=20, verbose_name="作業終了日")
    master = models.CharField(blank=True, null=True, max_length=30, verbose_name="委託業務責任者（甲）")
    middleman = models.CharField(blank=True, null=True, max_length=30, verbose_name="連絡窓口担当者（甲）")
    partner_master = models.CharField(
        max_length=30, blank=True, null=True, db_column='subcontractor_master', verbose_name="委託業務責任者（乙）"
    )
    partner_middleman = models.CharField(
        max_length=30, blank=True, null=True, db_column='subcontractor_middleman', verbose_name="連絡窓口担当者（乙）"
    )
    member_name = models.CharField(blank=True, null=True, max_length=30, verbose_name="作業責任者")
    location = models.CharField(blank=True, null=True, max_length=200, verbose_name="作業場所")
    is_hourly_pay = models.BooleanField(default=False, verbose_name="時給")
    is_fixed_cost = models.BooleanField(default=False, verbose_name="固定")
    is_show_formula = models.BooleanField(default=True, verbose_name="計算式")
    calculate_type_comment = models.CharField(max_length=255, blank=True, null=True, verbose_name="変動基準時間方式の説明")
    allowance_base = models.IntegerField(blank=True, null=True, verbose_name="基本給")
    allowance_base_memo = models.CharField(blank=True, null=True, max_length=255, verbose_name="基本給メモ")
    allowance_time_min = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, verbose_name="時間下限")
    allowance_time_max = models.DecimalField(blank=True, null=True, max_digits=5, decimal_places=2, verbose_name="時間上限")
    allowance_time_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="基準時間メモ")
    allowance_overtime = models.IntegerField(blank=True, null=True, verbose_name="残業手当")
    allowance_overtime_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="残業手当メモ")
    allowance_absenteeism = models.IntegerField(blank=True, null=True, verbose_name="欠勤手当")
    allowance_absenteeism_memo = models.CharField(max_length=255, blank=True, null=True, verbose_name="欠勤手当メモ")
    allowance_other = models.IntegerField(blank=True, null=True, verbose_name="その他手当")
    allowance_other_memo = models.CharField(blank=True, null=True, max_length=255, verbose_name="その他手当メモ")
    comment = models.CharField(max_length=2000, blank=True, null=True, verbose_name="備考")
    delivery_properties_comment = models.CharField(max_length=255, blank=True, null=True, verbose_name="納入物件")
    payment_condition_comments = models.CharField(max_length=2000, blank=True, null=True, verbose_name="支払条件")
    contract_items_comments = models.CharField(max_length=2000, blank=True, null=True, verbose_name="契約条項")

    class Meta:
        managed = False
        db_table = 'eb_bpmemberorderheading'
        default_permissions = ()
        verbose_name = "ＢＰ註文書見出し"
        verbose_name_plural = "ＢＰ註文書見出し一覧"

    def delete(self, using=None, keep_parents=False):
        return super(BaseModel, self).delete(using, keep_parents)
