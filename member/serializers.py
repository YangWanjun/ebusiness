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
        fields = '__all__'

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
        start_date = attrs.get('start_date')
        end_date = attrs.get('end_date')
        if end_date < start_date:
            raise serializers.ValidationError(constants.ERROR_DATE_CONTRADICT.format(start='開始日', end='終了日'))
        return attrs

    def validate_start_date(self, value):
        member = self.get_initial()['member']
        qs = models.OrganizationPeriod.objects.filter(member=member, start_date__lte=value, end_date__gte=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value

    def validate_end_date(self, value):
        member = self.get_initial()['member']
        qs = models.OrganizationPeriod.objects.filter(member=member, start_date__lte=value, end_date__gte=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value


class SalespersonSerializer(BaseModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True, label='名前')

    class Meta:
        model = models.Salesperson
        fields = '__all__'

    def get_full_name(self, obj):
        return obj.full_name


class SalespersonPeriodSerializer(BaseModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True, label='メンバー')
    salesperson_name = serializers.CharField(source='salesperson.full_name', read_only=True, label='営業員')

    class Meta:
        model = models.SalespersonPeriod
        fields = '__all__'
