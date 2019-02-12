from django.db import models

from utils import constants
from utils.models import AbstractCompany


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
        ordering = ['name']
        verbose_name = "取引先"
        verbose_name_plural = '取引先一覧'
