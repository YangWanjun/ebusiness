from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class PartnerSerializer(BaseModelSerializer):
    address = serializers.SerializerMethodField(label='所在地')

    class Meta:
        model = models.Partner
        fields = ('id', 'name', 'president', 'address', 'address1', 'tel', 'url')

    def get_address(self, obj):
        return obj.address

    get_address.sort_field = 'address1'
