from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class BusinessPartnerSerializer(BaseModelSerializer):
    address = serializers.SerializerMethodField(label='所在地')

    class Meta:
        model = models.BusinessPartner
        fields = ('id', 'name', 'president', 'address', 'tel')

    def get_address(self, obj):
        return obj.address
