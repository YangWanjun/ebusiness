from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db import models
from django.template import Context, Template
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from master.models import Company
from utils import constants, common
from utils.errors import CustomException
from utils.models import BaseModel


# Create your models here.
class MailTemplate(BaseModel):
    mail_title = models.CharField(max_length=50, unique=True, verbose_name="送信メールのタイトル")
    mail_body = models.TextField(blank=True, null=True, verbose_name="メール本文(Plain Text)")
    pass_title = models.CharField(
        max_length=50, blank=True, null=True, verbose_name="パスワード通知メールの題名",
        help_text='設定してない場合は「送信メールのタイトル」を使う。'
    )
    pass_body = models.TextField(blank=True, null=True, verbose_name="パスワードお知らせ本文(Plain Text)")
    description = models.TextField(blank=True, null=True, verbose_name="説明")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_mailtemplate'
        default_permissions = ()
        ordering = ('mail_title',)
        verbose_name = "メールテンプレート"
        verbose_name_plural = "メールテンプレート一覧"

    def __str__(self):
        return self.mail_title


class MailGroup(BaseModel):
    code = models.CharField(max_length=4, choices=constants.CHOICE_MAIL_GROUP, verbose_name="コード")
    name = models.CharField(max_length=30, unique=True, verbose_name="名称")
    title = models.CharField(max_length=50, blank=False, null=True, verbose_name="タイトル")
    sender = models.EmailField(db_column='mail_sender', verbose_name="メール差出人")
    sender_display_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="差出人表示名")
    template = models.ForeignKey(
        MailTemplate, blank=True, null=True, db_column='mail_template_id', on_delete=models.PROTECT,
        verbose_name="メールテンプレート"
    )
    footer = models.ForeignKey(
        MailTemplate, blank=True, null=True, on_delete=models.PROTECT, related_name='tail_group_set',
        verbose_name="フッター",
    )
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_mailgroup'
        default_permissions = ()
        ordering = ('title',)
        verbose_name = "メールグループ"
        verbose_name_plural = "メールグループ一覧"

    def __str__(self):
        return self.name

    def get_full_sender(self):
        if self.sender_display_name:
            return '{}<{}>'.format(self.sender_display_name, self.sender)
        else:
            return self.sender

    def get_cc_list(self):
        """メール送信時のＣＣ一覧を取得する。

        :return:
        """
        qs = MailCcList.objects.filter(group=self, is_bcc=False, is_deleted=False)
        return [item.email for item in qs]

    def get_bcc_list(self):
        """メール送信時のＢＣＣ一覧を取得する。

        :return:
        """
        qs = MailCcList.objects.filter(group=self, is_bcc=True, is_deleted=False)
        return [item.email for item in qs]

    @classmethod
    def get_mail_group_by_code(cls, code):
        """指定コードによってメールグループを取得する。

        :param code:
        :return:
        """
        try:
            return MailGroup.objects.get(code=code)
        except ObjectDoesNotExist:
            raise CustomException(constants.ERROR_MAIL_GROUP_NOT_FOUND.format(
                name=common.get_choice_name_by_key(constants.CHOICE_MAIL_GROUP, code)
            ))
        except MultipleObjectsReturned:
            raise CustomException(constants.ERROR_MAIL_GROUP_MULTI_FOUND.format(
                name=common.get_choice_name_by_key(constants.CHOICE_MAIL_GROUP, code)
            ))

    @classmethod
    def get_partner_order_group(cls):
        return cls.get_mail_group_by_code('0400')

    def get_template_content(self, context):
        """メールテンプレートの内容を取得する。

        :param context:
        :return:
        """
        if 'company' not in context:
            context['company'] = Company.get_company()
        ctx = Context(context)
        t_title = Template(context.get('mail_title') if 'mail_title' in context else self.template.mail_title)
        t_body = Template(context.get('mail_body') if 'mail_body' in context else self.template.mail_body)
        t_pwd_title = Template(self.template.pass_title) if self.template.pass_title else None
        t_password = Template(self.template.pass_body) if self.template.pass_body else None
        comment = self.template.description or ''
        title = t_title.render(ctx)
        body = t_body.render(ctx)
        ctx.update({'mail_title': title})
        if self.footer:
            footer = Template(self.footer.mail_body).render(ctx)
            body = common.join_html(body, footer)
        return {
            'index': context.get('index', None),            # 複数のメール同時送信時、indexが必要
            'sender': self.get_full_sender(),
            'user_name': context.get('user_name', None),    # 複数メール送信の場合、user_nameがタブ名とする
            'recipient': context.get('recipient', ''),
            'cc': context.get('cc', ''),
            'bcc': context.get('bcc', ''),
            'title': title,
            'body': body,
            'pwd_title': t_pwd_title.render(ctx) if t_pwd_title else '',
            'password': t_password.render(ctx) if t_password else '',
            'comment': comment,
        }

    def get_mail_data(self, context):
        """メール送信する

        :param context:
        :return:
        """
        content = self.get_template_content(context)
        cc_list = context.get('cc_list') if 'cc_list' in context else [cc.email for cc in self.get_cc_list()]
        bcc_list = context.get('bcc_list') if 'bcc_list' in context else [bcc.email for bcc in self.get_bcc_list()]
        return {
            'sender': self.get_full_sender(),
            'recipient_list': context.get('recipient'),
            'cc_list': cc_list,
            'bcc_list': bcc_list,
            'mail_title': content.get('title'),
            'mail_body': content.get('body'),
            'attachment_list': context.get('attachment_list'),
            'pass_title': content.get('pwd_title', None),
            'pass_body': content.get('password', None),
            'is_encrypt': context.get('is_encrypt', False),
        }


class MailCcList(BaseModel):
    group = models.ForeignKey(MailGroup, on_delete=models.CASCADE, verbose_name="メールグループ")
    email = models.EmailField(verbose_name="メールアドレス")
    is_bcc = models.BooleanField(default=False, verbose_name="ＢＣＣ")
    created_dt = models.DateTimeField(auto_now_add=True, db_column='created_date', verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, db_column='updated_date', verbose_name="更新日時")
    deleted_dt = models.DateTimeField(
        blank=True, null=True, editable=False, db_column='deleted_date', verbose_name="更新日時"
    )

    class Meta:
        managed = False
        db_table = 'eb_mailcclist'
        default_permissions = ()
        ordering = ('group', 'email')
        verbose_name = "メールＣＣリスト"
        verbose_name_plural = "メールＣＣリスト一覧"

    def __str__(self):
        return self.email


class EMailLogEntry(models.Model):
    action_time = models.DateTimeField(_('action time'), default=timezone.now, editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_('user'))
    sender = models.EmailField(verbose_name="差出人")
    recipient = models.CharField(max_length=1000, verbose_name="宛先")
    cc = models.CharField(max_length=1000, blank=True, null=True, verbose_name="ＣＣ")
    bcc = models.CharField(max_length=1000, blank=True, null=True, verbose_name="ＢＣＣ")
    title = models.CharField(max_length=50, verbose_name="件名")
    body = models.TextField(verbose_name="メール本文")
    attachment = models.CharField(max_length=255, blank=True, null=True, verbose_name="添付ファイル名")

    class Meta:
        managed = False
        db_table = 'eb_email_log'
        default_permissions = ()
        ordering = ('-action_time',)
        verbose_name = verbose_name_plural = "メール送信履歴"
