from django.db import models

from utils.models import BaseView


# Create your models here.
class TurnoverMonthly(BaseView):
    ym = models.CharField(max_length=6, verbose_name="対象年月")
    year = models.CharField(max_length=4, verbose_name="請求年")
    month = models.CharField(max_length=2, verbose_name="請求月")
    amount = models.IntegerField(verbose_name="合計")
    turnover_amount = models.IntegerField(verbose_name="売上（税別）")
    tax_amount = models.IntegerField(verbose_name="税金")
    expenses_amount = models.IntegerField(verbose_name="精算")

    class Meta:
        managed = False
        db_table = 'v_turnover_monthly'
        default_permissions = ()
        verbose_name = "月別売上"
        verbose_name_plural = "月別売上一覧"

    def __str__(self):
        return '{}年{}月'.format(self.year, self.month)

