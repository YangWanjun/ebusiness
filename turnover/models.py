from django.db import models

from utils.models import BaseView


# Create your models here.
class TurnoverMonthly(BaseView):
    ym = models.CharField(max_length=6, verbose_name="対象年月")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")

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
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")
    amount = models.IntegerField(verbose_name="合計")

    class Meta:
        managed = False
        db_table = 'v_turnover_yearly'
        ordering = ('year',)
        default_permissions = ()
        verbose_name = "年間売上"
        verbose_name_plural = "年間売上一覧"

    def __str__(self):
        return '{}年'.format(self.year,)
