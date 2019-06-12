import datetime
from decimal import Decimal

from django.db.models import Q

from rest_framework import serializers

from . import models
from utils import constants, common
from utils.rest_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):
    full_name = serializers.CharField(read_only=True, label='名前')
    full_kana = serializers.CharField(read_only=True, label='カナ')
    address = serializers.CharField(read_only=True, label='住所')

    class Meta:
        model = models.Member
        fields = '__all__'


class OrganizationSerializer(BaseModelSerializer):
    parent_name = serializers.CharField(source='parent.name', read_only=True, label='親組織')
    parent_url = serializers.SerializerMethodField(read_only=True, label='親組織のＵＲＬ')

    class Meta:
        model = models.Organization
        fields = '__all__'

    def get_parent_url(self, obj):
        return '/organization/{pk}'.format(pk=obj.parent.pk) if obj.parent else None


class PositionShipSerializer(BaseModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True, label='メンバー')
    organization_name = serializers.CharField(source='organization.name', read_only=True, label='部署名称')
    position = serializers.CharField(label='職位')

    class Meta:
        model = models.PositionShip
        fields = '__all__'

    def validate_position(self, value):
        organization = models.Organization.objects.get(pk=self.get_initial()['organization'])
        if organization.org_type == '01' and value not in ('3.0', '3.1'):
            raise serializers.ValidationError(constants.ERROR_ORGANIZATION_POSITION.format(
                org_type='事業部', value=common.get_choice_name_by_key(constants.CHOICE_POSITION, Decimal(value)),
            ))
        elif organization.org_type == '02' and value not in ('4.0', '5.0'):
            raise serializers.ValidationError(constants.ERROR_ORGANIZATION_POSITION.format(
                org_type='部署', value=common.get_choice_name_by_key(constants.CHOICE_POSITION, Decimal(value)),
            ))
        elif organization.org_type == '03' and value not in ('6.0', '7.0'):
            raise serializers.ValidationError(constants.ERROR_ORGANIZATION_POSITION.format(
                org_type='課', value=common.get_choice_name_by_key(constants.CHOICE_POSITION, Decimal(value)),
            ))
        return value


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
        end_date = attrs.get('end_date') or datetime.date.max
        if end_date < start_date:
            raise serializers.ValidationError(constants.ERROR_DATE_CONTRADICT.format(start='開始日', end='終了日'))
        return attrs

    def validate_start_date(self, value):
        member = self.get_initial()['member']
        qs = models.OrganizationPeriod.objects.filter(
            Q(end_date__gte=value) | Q(end_date__isnull=True), member=member, start_date__lte=value
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value

    def validate_end_date(self, value):
        member = self.get_initial()['member']
        qs = models.OrganizationPeriod.objects.filter(
            Q(end_date__gte=value) | Q(end_date__isnull=True), member=member, start_date__lte=value
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value


class SalespersonSerializer(BaseModelSerializer):

    class Meta:
        model = models.Salesperson
        fields = '__all__'


class SalespersonPeriodSerializer(BaseModelSerializer):
    member_name = serializers.CharField(source='member.full_name', read_only=True, label='メンバー')
    salesperson_name = serializers.CharField(source='salesperson.name', read_only=True, label='営業員')

    class Meta:
        model = models.SalespersonPeriod
        fields = '__all__'

    def validate_start_date(self, value):
        member = self.get_initial()['member']
        qs = models.SalespersonPeriod.objects.filter(
            Q(end_date__gte=value) | Q(end_date__isnull=True), member=member, start_date__lte=value
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value

    def validate_end_date(self, value):
        member = self.get_initial()['member']
        qs = models.SalespersonPeriod.objects.filter(
            Q(end_date__gte=value) | Q(end_date__isnull=True), member=member, start_date__lte=value
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if member and qs.count() > 0:
            raise serializers.ValidationError(constants.ERROR_DATE_CONFLICT.format(date=value))
        return value
