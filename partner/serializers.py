from rest_framework import serializers

from . import models
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
