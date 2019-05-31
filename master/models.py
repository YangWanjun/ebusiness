import os
import uuid

from django.core.exceptions import ObjectDoesNotExist
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from utils import common
from utils.models import BaseModel, AbstractCompany, AbstractBankAccount


class Company(AbstractCompany):
    kana = models.CharField(max_length=30, blank=True, null=True, db_column='japanese_spell', verbose_name="フリカナ")

    class Meta:
        managed = False
        db_table = 'eb_company'
        default_permissions = ()
        verbose_name = verbose_name_plural = "自社情報"


class Bank(BaseModel):
    code = models.CharField(
        max_length=4, primary_key=True, validators=(RegexValidator(regex=r'[0-9]{4}'),), verbose_name="金融機関コード"
    )
    name = models.CharField(max_length=30, verbose_name="金融機関名称")
    kana = models.CharField(
        max_length=30, blank=True, null=True, verbose_name="金融機関カナ",
        help_text="半角カナ文字及び英数字等、左詰め残りスペースとする。"
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bank'
        ordering = ['code']
        default_permissions = ()
        verbose_name = "金融機関"
        verbose_name_plural = "金融機関一覧"

    def __str__(self):
        return self.name


# class BankBranch(BaseModel):
#     bank = models.ForeignKey(Bank, on_delete=models.PROTECT, verbose_name="銀行")
#     branch_no = models.CharField(max_length=3, validators=(RegexValidator(regex=r'[0-9]{3}'),), verbose_name="支店番号")
#     branch_name = models.CharField(max_length=20, verbose_name="支店名称")
#     branch_kana = models.CharField(
#         max_length=40, blank=True, null=True, verbose_name="支店カナ",
#         help_text="半角カナ文字及び英数字等、左詰め残りスペースとする。",
#     )
#     address = models.CharField(max_length=200, blank=True, null=True, verbose_name="所在地")
#     tel = models.CharField(
#         max_length=15, blank=True, null=True, verbose_name="電話番号",
#         validators=(RegexValidator(regex=constants.REG_TEL),)
#     )
#
#     class Meta:
#         db_table = 'mst_bank_branch'
#         ordering = ['bank', 'branch_no']
#         verbose_name = "銀行支店"
#         verbose_name_plural = "銀行支店一覧"
#
#     def __str__(self):
#         return self.branch_name


class BankAccount(AbstractBankAccount):
    bank = models.ForeignKey(Bank, verbose_name="銀行", on_delete=models.PROTECT)
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_bankinfo'
        default_permissions = ()
        verbose_name = "銀行口座"
        verbose_name_plural = "銀行口座一覧"

    def __str__(self):
        return self.account_number


class ProjectStage(BaseModel):
    name = models.CharField(max_length=15, unique=True, verbose_name="作業工程名称")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'mst_project_stage'
        default_permissions = ()
        verbose_name = "作業工程"
        verbose_name_plural = '作業工程一覧'

    def __str__(self):
        return self.name


class ExpensesCategory(BaseModel):
    name = models.CharField(max_length=50, unique=True, verbose_name="名称")

    class Meta:
        managed = False
        verbose_name = "精算分類"
        verbose_name_plural = "精算分類一覧"
        db_table = 'mst_expenses_category'

    def __str__(self):
        return self.name


class Holiday(BaseModel):
    date = models.DateField(unique=True, verbose_name="日付")
    comment = models.CharField(max_length=100, verbose_name="説明")

    class Meta:
        managed = False
        db_table = 'mst_holiday'
        ordering = ('date',)
        verbose_name = "休日"
        verbose_name_plural = "休日一覧"


def get_attachment_id():
    return '{time}_{uuid}'.format(
        time=timezone.now().strftime('%y%m%d%H%M%S'),
        uuid=uuid.uuid4(),
    )


class Attachment(BaseModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    uuid = models.CharField(max_length=55, unique=True, default=get_attachment_id, verbose_name="ファイルの唯一ＩＤ")
    name = models.CharField(max_length=100, verbose_name="帳票名称")
    path = models.FileField(upload_to=common.get_attachment_path)

    class Meta:
        managed = False
        db_table = 'mst_attachment'
        default_permissions = ()
        verbose_name = "ファイル"
        verbose_name_plural = "ファイル一覧"

    @classmethod
    def save_from_bytes(cls, content_object, byte_file, filename, existed_file=None):
        if existed_file:
            try:
                cls.objects.get(uuid=existed_file).delete()
            except ObjectDoesNotExist:
                pass
        byte_file.seek(0)
        uploaded_file = ContentFile(byte_file.read())
        uploaded_file.name = filename
        attachment = cls.objects.create(
            content_object=content_object,
            name=filename,
            path=uploaded_file
        )
        return attachment

    def delete(self, using=None, keep_parents=False):
        if os.path.exists(self.path.path):
            os.remove(self.path.path)
        super(Attachment, self).delete(using, keep_parents)
