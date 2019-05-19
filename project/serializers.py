from django.utils import timezone

from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class ClientSerializer(BaseModelSerializer):

    class Meta:
        model = models.Client
        fields = '__all__'


class ClientMemberSerializer(BaseModelSerializer):
    client__name = serializers.CharField(source='client.name', read_only=True, label='所属会社')

    class Meta:
        model = models.ClientMember
        fields = '__all__'


class ProjectSerializer(BaseModelSerializer):
    client__name = serializers.CharField(source='client.name', read_only=True, label='関連会社')
    manager__name = serializers.CharField(source='manager.name', read_only=True, label='案件責任者')
    contact__name = serializers.CharField(source='contact.name', read_only=True, label='案件連絡者')
    organization__name = serializers.CharField(source='organization.name', read_only=True, label='所属部署')
    decimal_type = serializers.CharField(source='client.decimal_type', read_only=True, label='小数の処理区分')
    tax_rate = serializers.DecimalField(
        source='client.tax_rate', max_digits=3, decimal_places=2, read_only=True, label='税率'
    )

    class Meta:
        model = models.Project
        fields = '__all__'


class VProjectSerializer(BaseModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.VProject
        fields = '__all__'

    def get_url(self, obj):
        return '/project/{pk}/'.format(pk=obj.pk,)


class ProjectMemberSerializer(BaseModelSerializer):
    member_name = serializers.SerializerMethodField(read_only=True, label='名前')
    project__name = serializers.CharField(source='project.name', read_only=True, label='案件名称')
    is_working = serializers.SerializerMethodField(read_only=True, label='稼働中')

    class Meta:
        model = models.ProjectMember
        fields = '__all__'

    def get_member_name(self, obj):
        return '{} {}'.format(obj.member.first_name, obj.member.last_name)

    def get_is_working(self, obj):
        return obj and obj.end_date is None or obj.end_date >= timezone.now().date()

    get_is_working.field_type = 'boolean'


class MemberAttendanceSerializer(BaseModelSerializer):

    class Meta:
        model = models.MemberAttendance
        fields = '__all__'


class ClientOrderSerializer(BaseModelSerializer):

    class Meta:
        model = models.ClientOrder
        fields = '__all__'
