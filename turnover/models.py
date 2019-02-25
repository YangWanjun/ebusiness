from django.db import models

from member.models import Organization
from project.models import Client, Project
from utils.models import BaseView


# Create your models here.
class TurnoverMonthly(BaseView):
    ym = models.CharField(max_length=6, verbose_name="対象年月")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_monthly'
        ordering = ('-ym',)
        default_permissions = ()
        verbose_name = "月別売上"
        verbose_name_plural = "月別売上一覧"

    def __str__(self):
        return '{}年{}月'.format(self.year, self.month)


class TurnoverYearly(BaseView):
    year = models.CharField(max_length=4, primary_key=True, verbose_name="請求年")
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_yearly'
        ordering = ('year',)
        default_permissions = ()
        verbose_name = "年間売上"
        verbose_name_plural = "年間売上一覧"

    def __str__(self):
        return '{}年'.format(self.year,)


class TurnoverMonthlyByOrganization(BaseView):
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    division = models.ForeignKey(
        Organization, null=True, on_delete=models.DO_NOTHING, related_name='division_monthly_turnover_set',
        verbose_name="事業部"
    )
    organization = models.ForeignKey(
        Organization, null=True, on_delete=models.DO_NOTHING, related_name='organization_monthly_turnover_set',
        verbose_name="部署"
    )
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_monthly_by_organization'
        ordering = ('year', 'month')
        default_permissions = ()
        verbose_name = "部署月別売上"
        verbose_name_plural = "部署月別売上一覧"

    def __str__(self):
        return '{}年{}月'.format(self.year, self.month)


class TurnoverClientsByMonth(BaseView):
    client_name = models.CharField(max_length=30, verbose_name="会社名")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_clients_by_month'
        ordering = ('client_name',)
        default_permissions = ()
        verbose_name = "お客様別売上"
        verbose_name_plural = "お客様別売上一覧"

    def __str__(self):
        return self.client_name


class TurnoverClientByMonth(BaseView):
    project_name = models.CharField(max_length=50, verbose_name="案件名")
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="会社ID")
    client_name = models.CharField(max_length=30, verbose_name="会社名")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_client_by_month'
        ordering = ('project_name',)
        default_permissions = ()
        verbose_name = "案件別売上"
        verbose_name_plural = "案件別売上一覧"

    def __str__(self):
        return self.project_name


class TurnoverMember(BaseView):
    name = models.CharField(max_length=50, verbose_name="社員")
    organization = models.ForeignKey(
        Organization, db_column='member_section_id', on_delete=models.DO_NOTHING, verbose_name="所属"
    )
    org_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="所属名称")
    project = models.ForeignKey(Project, on_delete=models.DO_NOTHING, verbose_name="案件")
    client = models.ForeignKey(Client, on_delete=models.DO_NOTHING, verbose_name="取引先")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    cost = models.IntegerField(verbose_name="コスト")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    expenses_amount = models.IntegerField(verbose_name="精算")
    profit_amount = models.IntegerField(verbose_name="粗利")
    profit_rate = models.DecimalField(max_digits=4, decimal_places=1, verbose_name="利率")

    class Meta:
        managed = False
        db_table = 'v_turnover_member'
        ordering = ('name',)
        default_permissions = ()
        verbose_name = "社員売上"
        verbose_name_plural = "社員売上一覧"

    def __str__(self):
        return self.name
