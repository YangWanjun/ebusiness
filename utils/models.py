from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

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


class BaseView(models.Model):
    objects = DefaultManager()

    class Meta:
        abstract = True
        default_permissions = ()


class AbstractCompany(BaseModel):
    name = models.CharField(max_length=30, blank=False, null=False, unique=True, verbose_name="会社名")
    kana = models.CharField(max_length=30, blank=True, null=True, verbose_name="フリカナ")
    president = models.CharField(max_length=30, blank=True, null=True, verbose_name="代表者名")
    found_date = models.DateField(blank=True, null=True, verbose_name="設立年月日")
    capital = models.BigIntegerField(blank=True, null=True, verbose_name="資本金")
    post_code = models.CharField(
        blank=True, null=True, max_length=8, verbose_name="郵便番号",
        validators=(RegexValidator(regex=constants.REG_POST_CODE),),
    )
    address1 = models.CharField(max_length=200, blank=True, null=True, verbose_name="住所１")
    address2 = models.CharField(max_length=200, blank=True, null=True, verbose_name="住所２")
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
        ordering = ('name',)

    def __str__(self):
        return self.name

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')


class AbstractMember(BaseModel):
    last_name = models.CharField(max_length=10, verbose_name="姓")
    first_name = models.CharField(max_length=10, verbose_name="名")
    last_name_ja = models.CharField(blank=True, null=True, max_length=30, verbose_name="姓(フリカナ)")
    first_name_ja = models.CharField(blank=True, null=True, max_length=30, verbose_name="名(フリカナ)")
    last_name_en = models.CharField(
        blank=True, null=True, max_length=30, verbose_name="姓(ローマ字)",
        help_text="漢字ごとに先頭文字は大文字にしてください（例：XiaoWang）"
    )
    first_name_en = models.CharField(
        blank=True, null=True, max_length=30, verbose_name="名(ローマ字)",
        help_text="先頭文字は大文字にしてください（例：Zhang）"
    )
    gender = models.CharField(blank=True, null=True, max_length=1, choices=constants.CHOICE_SEX, verbose_name="性別")
    country = models.CharField(blank=True, null=True, max_length=20, verbose_name="国籍・地域")
    birthday = models.DateField(blank=True, null=True, verbose_name="生年月日")
    graduate_date = models.DateField(blank=True, null=True, verbose_name="卒業年月日")
    join_date = models.DateField(blank=True, null=True, default=timezone.now, verbose_name="入社年月日")
    email = models.EmailField(blank=True, null=True, verbose_name="会社メールアドレス")
    private_email = models.EmailField(blank=True, null=True, verbose_name="個人メールアドレス")
    post_code = models.CharField(
        blank=True, null=True, max_length=8, verbose_name="郵便番号",
        validators=(RegexValidator(regex=constants.REG_POST_CODE),),
        help_text="数値だけを入力してください、例：1230034"
    )
    address1 = models.CharField(blank=True, null=True, max_length=200, verbose_name="住所１")
    address2 = models.CharField(blank=True, null=True, max_length=200, verbose_name="住所２")
    lat = models.CharField(blank=True, null=True, max_length=25, verbose_name="緯度")
    lng = models.CharField(blank=True, null=True, max_length=25, verbose_name="経度")
    nearest_station = models.CharField(blank=True, null=True, max_length=15, verbose_name="最寄駅")
    years_in_japan = models.IntegerField(blank=True, null=True, verbose_name="在日年数")
    phone = models.CharField(
        blank=True, null=True, max_length=15, verbose_name="携帯番号",
        validators=(RegexValidator(regex=constants.REG_PHONE),),
        help_text="数値だけを入力してください、例：08012345678"
    )
    marriage = models.CharField(
        max_length=1, blank=True, null=True, choices=constants.CHOICE_MARRIED, verbose_name="婚姻状況"
    )
    japanese_description = models.CharField(max_length=250, blank=True, null=True, verbose_name="日本語能力の説明")
    certificate = models.CharField(max_length=250, blank=True, null=True, verbose_name="資格の説明")
    skill_description = models.CharField(max_length=250, blank=True, null=True, verbose_name="得意")
    comment = models.CharField(max_length=250, blank=True, null=True, verbose_name="備考")

    class Meta:
        abstract = True

    @property
    def address(self):
        return '{}{}'.format(self.address1 or '', self.address2 or '')
