import os
import mimetypes
import zipfile
import traceback
import subprocess
import io
import datetime
import shutil
import sys

from email import encoders
from email.header import Header

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives, get_connection, SafeMIMEText
from django.core.mail.message import MIMEBase
from django.core.validators import validate_email
from django.db import connection
from django.utils.encoding import smart_str

from .models import EMailLogEntry
from master.models import Attachment
from utils import constants, common
from utils.errors import CustomException


logger = common.get_system_logger()


class Mail(object):
    def __init__(self, sender=None, recipient_list=None, cc_list=None, bcc_list=None, attachment_list=None,
                 is_encrypt=False, mail_title=None, mail_body=None, pass_title=None, pass_body=None, **kwargs):
        self.sender = sender
        self.recipient_list = Mail.str_to_list(recipient_list)
        self.cc_list = Mail.str_to_list(cc_list)
        self.bcc_list = Mail.str_to_list(bcc_list)
        self.attachment_list = attachment_list if attachment_list else []
        self.is_encrypt = is_encrypt
        self.mail_title = mail_title
        self.mail_body = mail_body
        self.pass_title = pass_title
        self.password = None
        self.pass_body = pass_body
        self.temp_files = []

    def check_recipient(self):
        if not self.recipient_list:
            raise CustomException("宛先はありません。")
        return self.check_email_address(self.recipient_list)

    def check_cc_list(self):
        return self.check_email_address(self.cc_list)

    def check_bcc_list(self):
        return self.check_email_address(self.bcc_list)

    def check_attachment(self):
        if self.attachment_list:
            qs = Attachment.objects.filter(is_deleted=False, uuid__in=self.attachment_list)
            self.attachment_list = [AttachmentFile(path=item.path.path, filename=item.name) for item in qs]
            for attachment in self.attachment_list:
                if not attachment.is_valid():
                    raise CustomException("ファイル「%s」が見つかりません。" % attachment)

    def check_mail_title(self):
        if not self.mail_title:
            raise CustomException("メールの題名を設定してください。")

    @classmethod
    def get_mail_connection(cls):
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s "
                    " union all "
                    "select value from mst_config where name = %s ",
                    [constants.CONFIG_EMAIL_SMTP_HOST, constants.CONFIG_EMAIL_SMTP_PORT,
                     constants.CONFIG_EMAIL_ADDRESS, constants.CONFIG_EMAIL_PASSWORD]
                )
                host, port, username, password = cursor.fetchall()
            backend = get_connection()
            backend.host = str(host[0])
            backend.port = int(port[0])
            backend.username = str(username[0])
            backend.password = str(password[0])
            return backend
        except Exception as ex:
            logger.error(str(ex))
            logger.error(traceback.format_exc())
            raise CustomException(str(ex))

    @classmethod
    def str_to_list(cls, s):
        if isinstance(s, str):
            return [i.strip() for i in s.split(',') if i]
        else:
            return s

    @classmethod
    def check_email_address(cls, mail_address):
        if not mail_address:
            return False
        if isinstance(mail_address, str):
            mail_list = [mail_address]
        elif isinstance(mail_address, (tuple, list)):
            mail_list = mail_address
        else:
            raise CustomException('有効なメールアドレスを入れてください。')

        for email in mail_list:
            try:
                validate_email(email)
            except ValidationError:
                raise CustomException('有効なメールアドレスを入れてください。')
        return True

    def zip_attachments(self):
        if self.attachment_list:
            if sys.platform in ("linux", "linux2"):
                # tempフォルダー配下の一時フォルダーを取得する
                temp_path = os.path.join(common.get_temp_path(), datetime.datetime.now().strftime('%Y%m%d%H%M%S%f'))
                if not os.path.exists(temp_path):
                    os.mkdir(temp_path)
                    self.temp_files.append(temp_path)
                temp_zip = os.path.join(common.get_temp_path(), datetime.datetime.now().strftime('%Y%m%d%H%M%S%f.zip'))
                self.temp_files.append(temp_zip)
                file_list = []
                for attachment_file in self.attachment_list:
                    new_path = os.path.join(temp_path, attachment_file.filename)
                    file_list.append(new_path)
                    self.temp_files.append(new_path)
                    if attachment_file.is_bytes():
                        # バイナリーファイルを一時ファイルに書き込む
                        with open(new_path, 'wb') as f:
                            f.write(attachment_file.content)
                    else:
                        shutil.copy(attachment_file.path, new_path)
                password = self.generate_password()
                # tempフォルダー配下すべてのファイル名をUTF8からShift-JISに変換する
                subprocess.call(["convmv", "-r", "-f", "utf8", '-t', 'sjis', '--notest', temp_path.rstrip('/') + '/'])
                # 一時フォルダーを圧縮する
                command = "zip --password {0} -j {1} {2}/*".format(password, temp_zip, temp_path.rstrip('/'))
                print(command)
                subprocess.call(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                bytes_data = open(temp_zip, 'rb', ).read()
                return bytes_data
            else:
                buff = io.BytesIO()
                in_memory_zip = zipfile.ZipFile(buff, mode='w')
                for attachment_file in self.attachment_list:
                    if attachment_file.is_bytes():
                        in_memory_zip.writestr(attachment_file.filename, attachment_file.content)
                    else:
                        in_memory_zip.write(attachment_file.path, attachment_file.filename)
                in_memory_zip.close()
                return buff.getvalue()
        else:
            return None

    # def escape(self, name):
    #     """Shift_JISのダメ文字対策
    #
    #     2バイト目に「5C」のコードが使われている文字は、次のようなものがあります。
    #     ―ソЫⅨ噂浬欺圭構蚕十申曾箪貼能表暴予禄兔喀媾彌拿杤歃濬畚秉綵臀藹觸軆鐔饅鷭偆砡
    #
    #     :param name:
    #     :return:
    #     """
    #     chars = "ソЫⅨ噂浬欺圭構蚕十申曾箪貼能表暴予禄兔喀媾彌拿杤歃濬畚秉綵臀藹觸軆鐔饅鷭偆砡"
    #     s = name
    #     for c in chars:
    #         if c in s:
    #             s = s.replace(c, "＿")
    #     return s

    def generate_password(self, length=8):
        self.password = common.generate_password(length)
        return self.password

    def send_email(self, user=None):
        try:
            self.check_recipient()
            self.check_cc_list()
            self.check_bcc_list()
            self.check_attachment()
            self.check_mail_title()

            mail_connection = self.get_mail_connection()
            if not self.sender:
                self.sender = mail_connection.username

            email = EmailMultiAlternativesWithEncoding(
                subject=self.mail_title,
                body=self.mail_body,
                from_email=self.sender,
                to=self.recipient_list,
                cc=self.cc_list,
                bcc=self.bcc_list,
                connection=mail_connection
            )
            # email.attach_alternative(self.mail_body, constants.MIME_TYPE_HTML)
            if self.is_encrypt is False:
                for attachment in [item for item in self.attachment_list]:
                    if attachment.is_bytes():
                        email.attach(attachment.filename, attachment.content, constants.MIME_TYPE_ZIP)
                    else:
                        email.attach_file(attachment.path, constants.MIME_TYPE_STREAM)
            else:
                attachments = self.zip_attachments()
                if attachments:
                    email.attach('%s.zip' % self.mail_title, attachments, constants.MIME_TYPE_ZIP)
            email.send()
            # パスワードを送信する。
            self.send_password(mail_connection, user=user)
            log_format = "題名: %s; TO: %s; CC: %s; 送信完了。"
            logger.info(log_format % (
                self.mail_title,
                ','.join(self.recipient_list) if self.recipient_list else '',
                ','.join(self.cc_list) if self.cc_list else ''
            ))

            if user:
                # 送信ログ
                if self.attachment_list:
                    attachment_name = ",".join([item.filename for item in self.attachment_list])
                else:
                    attachment_name = None
                EMailLogEntry.objects.create(
                    user=user,
                    sender=self.sender,
                    recipient=",".join(self.recipient_list),
                    cc=",".join(self.cc_list) if self.cc_list else None,
                    bcc=",".join(self.bcc_list) if self.bcc_list else None,
                    title=self.mail_title,
                    body=self.mail_body,
                    attachment=attachment_name,
                )
        except subprocess.CalledProcessError as e:
            logger.error(e.output)
            logger.error(traceback.format_exc())
            raise CustomException(str(e.output))
        except Exception as ex:
            logger.error(ex)
            logger.error(traceback.format_exc())
            raise CustomException(str(ex))
        finally:
            # 一時ファイルを削除
            for path in self.temp_files:
                if os.path.exists(path):
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    else:
                        os.remove(path)

    def send_password(self, conn, user=None):
        if self.attachment_list and self.is_encrypt and self.password:
            subject = self.pass_title or self.mail_title
            try:
                body = self.pass_body.format(password=self.password)
            except Exception as ex:
                logger.error(ex)
                body = "PW: %s" % self.password
            email = EmailMultiAlternativesWithEncoding(
                subject=subject,
                body=body,
                from_email=self.sender,
                to=self.recipient_list,
                cc=self.cc_list,
                connection=conn
            )
            # email.attach_alternative(body, constants.MIME_TYPE_HTML)
            email.send()
            logger.info("%sのパスワードは送信しました。" % self.mail_title)
            if user:
                # パスワード送信ログ
                EMailLogEntry.objects.create(
                    user=user,
                    sender=self.sender,
                    recipient=",".join(self.recipient_list),
                    cc=",".join(self.cc_list) if self.cc_list else None,
                    bcc=",".join(self.bcc_list) if self.bcc_list else None,
                    title=subject,
                    body=body,
                    attachment=None,
                )


class AttachmentFile:

    def __init__(self, path=None, content=None, filename=None):
        self.path = path
        self.content = content
        if path and not filename:
            self.filename = os.path.basename(path)
        else:
            self.filename = filename

    def is_valid(self):
        """有効なファイルであるかどうか

        :return:
        """
        if self.path:
            return os.path.exists(self.path)
        elif self.content and isinstance(self.content, bytes):
            return True
        else:
            return False

    def is_bytes(self):
        if self.content and isinstance(self.content, bytes):
            return True
        else:
            return False


class EmailMultiAlternativesWithEncoding(EmailMultiAlternatives):
    def _create_attachment(self, filename, content, mimetype=None):
        """
        Converts the filename, content, mimetype triple into a MIME attachment
        object. Use self.encoding when handling text attachments.
        """
        if mimetype is None:
            mimetype, _ = mimetypes.guess_type(filename)
            # if mimetype is None:
            #     mimetype = constants.MIME_TYPE_EXCEL
        basetype, subtype = mimetype.split('/', 1)
        if basetype == 'text':
            encoding = self.encoding or settings.DEFAULT_CHARSET
            attachment = SafeMIMEText(smart_str(content, settings.DEFAULT_CHARSET), subtype, encoding)
        else:
            # Encode non-text attachments with base64.
            attachment = MIMEBase(basetype, subtype)
            attachment.set_payload(content)
            encoders.encode_base64(attachment)
        if filename:
            try:
                filename = Header(filename, 'utf-8').encode()
            except Exception as ex:
                logger.error(ex)
                logger.error(traceback.format_exc())
            attachment.add_header('Content-Disposition', 'attachment', filename=filename)
        return attachment
