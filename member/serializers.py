from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True, label='名前')
    full_kana = serializers.SerializerMethodField(read_only=True, label='カナ')
    address = serializers.SerializerMethodField(read_only=True, label='住所')
    gender = serializers.CharField(source='get_gender_display', read_only=True, label='性別')

    class Meta:
        model = models.Member
        fields = (
            'id',
            'full_name',
            'last_name',
            'first_name',
            'full_kana',
            'gender',
            'address',
            'address1',
            'birthday',
            'join_date',
            'japanese_description',
            'certificate',
            'skill_description',
            'comment',
            'avatar_url',
        )

    def get_full_name(self, obj):
        return obj.full_name

    def get_full_kana(self, obj):
        return obj.full_kana

    def get_address(self, obj):
        return obj.address

    get_full_name.sort_field = 'last_name'
    get_address.sort_field = 'address1'


class OrganizationSerializer(BaseModelSerializer):
    class Meta:
        model = models.Organization
        fields = '__all__'
