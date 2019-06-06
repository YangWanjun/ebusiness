from rest_framework import serializers

from . import models
from member.models import Member
from utils import constants
from utils.rest_base import BaseModelSerializer


class PartnerSerializer(BaseModelSerializer):
    address = serializers.SerializerMethodField(read_only=True, label='住所')

    class Meta:
        model = models.Partner
        fields = '__all__'

    def get_address(self, obj):
        return obj.address


class PartnerEmployeeSerializer(BaseModelSerializer):

    class Meta:
        model = models.PartnerEmployee
        fields = '__all__'


class PartnerPayNotifyRecipientSerializer(BaseModelSerializer):
    member_name = serializers.CharField(source='member.name', read_only=True, label='名前')
    email = serializers.CharField(source='member.email', read_only=True, label='メールアドレス')

    class Meta:
        model = models.PartnerPayNotifyRecipient
        fields = '__all__'


class PartnerBankAccountSerializer(BaseModelSerializer):
    bank_name = serializers.CharField(source='bank.name', read_only=True, label='銀行名称')

    class Meta:
        model = models.PartnerBankAccount
        fields = '__all__'


class BpContractSerializer(BaseModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True, label='会社名')

    class Meta:
        model = models.BpContract
        fields = '__all__'

    def validate_start_date(self, value):
        member = Member.objects.get(pk=self.get_initial()['member'])
        qs = member.bpcontract_set.filter(start_date__lte=value, end_date__gte=value, is_deleted=False)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value

    def validate_end_date(self, value):
        member = Member.objects.get(pk=self.get_initial()['member'])
        qs = member.bpcontract_set.filter(start_date__lte=value, end_date__gte=value, is_deleted=False)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value


class BpMemberOrderSerializer(BaseModelSerializer):

    class Meta:
        model = models.BpMemberOrder
        fields = '__all__'
