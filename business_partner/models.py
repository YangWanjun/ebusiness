from django.db import models

from utils import constants
from utils.models import AbstractCompany


class BusinessPartner(AbstractCompany):
    employee_count = models.IntegerField(blank=True, null=True, verbose_name="従業員数")
    sales_amount = models.BigIntegerField(blank=True, null=True, verbose_name="売上高")
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

    class Meta:
        db_table = 'eb_business_partner'
        verbose_name = "協力会社"
        verbose_name_plural = '協力会社一覧'
