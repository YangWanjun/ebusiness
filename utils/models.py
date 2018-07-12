from django.core.validators import RegexValidator
from django.db import models

from utils import constants


class DefaultManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(DefaultManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_queryset(self):
        return super(DefaultManager, self).get_queryset().filter(*self.args, **self.kwargs)


class BaseModel(models.Model):
    created_dt = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    objects = DefaultManager()

    class Meta:
        abstract = True


class AbstractCompany(BaseModel):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True, verbose_name="会社名")
    kana = models.CharField(blank=True, null=True, max_length=30, verbose_name="フリカナ")
    president = models.CharField(blank=True, null=True, max_length=30, verbose_name="代表者名")
    found_date = models.DateField(blank=True, null=True, verbose_name="設立年月日")
    capital = models.BigIntegerField(blank=True, null=True, verbose_name="資本金")
    post_code = models.CharField(
        blank=True, null=True, max_length=8, verbose_name="郵便番号",
        validators=(RegexValidator(regex=constants.REG_POST_CODE),),
    )
    address1 = models.CharField(blank=True, null=True, max_length=200, verbose_name="住所１")
    address2 = models.CharField(blank=True, null=True, max_length=200, verbose_name="住所２")
    tel = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="電話番号",
        validators=(RegexValidator(regex=constants.REG_TEL),)
    )
    fax = models.CharField(
        max_length=15, blank=True, null=True, verbose_name="ファックス",
        validators=(RegexValidator(regex=constants.REG_FAX),)
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')
