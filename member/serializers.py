from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):
    full_name = serializers.SerializerMethodField(label='名前')
    address = serializers.SerializerMethodField(label='住所')

    class Meta:
        model = models.Member
        fields = ('id', 'full_name', 'gender', 'address', 'birthday', 'join_date')

    def get_full_name(self, obj):
        return obj.full_name

    def get_address(self, obj):
        return obj.address
