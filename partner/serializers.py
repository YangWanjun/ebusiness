from rest_framework import serializers

from . import models
from member.models import Member
from utils import constants, common
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


class BpMemberOrderDisplaySerializer(BaseModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    business_days = serializers.SerializerMethodField()
    order_file = serializers.CharField(source='filename')
    order_request_file = serializers.CharField(source='filename_request')
    order_url = serializers.SerializerMethodField(read_only=True)
    parent = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = models.BpMemberOrder
        fields = (
            'id', 'name', 'year', 'month', 'end_year', 'end_month', 'business_days', 'order_no',
            'order_file', 'order_request_file',
            'order_url', 'is_sent', 'parent',
        )

    def get_name(self, obj):
        return '{}年{}月'.format(obj.year, obj.month)

    def get_business_days(self, obj):
        if obj.business_days:
            return obj.business_days
        else:
            return len(common.get_business_days(obj.year, obj.month))

    def get_order_url(self, obj):
        return '/partner/{partner_id}/members/{member_id}/orders/{order_id}'.format(
            partner_id=90,
            member_id=obj.project_member.member.pk,
            order_id=obj.pk
        )

    def get_parent(self, obj):
        return obj.project_member.pk
