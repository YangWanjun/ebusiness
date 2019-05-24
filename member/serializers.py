from rest_framework import serializers

from . import models
from utils import constants
from utils.rest_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True, label='名前')
    full_kana = serializers.SerializerMethodField(read_only=True, label='カナ')
    address = serializers.SerializerMethodField(read_only=True, label='住所')

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


class OrganizationPeriodSerializer(BaseModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True, label='メンバー')
    division_name = serializers.CharField(source='division.name', read_only=True, label='事業部名称')
    department_name = serializers.CharField(source='department.name', read_only=True, label='部署名称')
    section_name = serializers.CharField(source='section.name', read_only=True, label='課名称')

    class Meta:
        model = models.OrganizationPeriod
        fields = '__all__'

    def validate(self, attrs):
        division = attrs.get('division')
        department = attrs.get('department')
        section = attrs.get('section')
        if division is None and department is None and section is None:
            raise serializers.ValidationError(constants.ERROR_REQUIRE_FIELD.format(name='所属部署'))
        return attrs
