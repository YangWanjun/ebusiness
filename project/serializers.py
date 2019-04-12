from django.utils import timezone

from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class ClientSerializer(BaseModelSerializer):

    class Meta:
        model = models.Client
        fields = '__all__'


class ClientMemberSerializer(BaseModelSerializer):

    class Meta:
        model = models.ClientMember
        fields = '__all__'


class ProjectSerializer(BaseModelSerializer):
    client = ClientSerializer()
    client__name = serializers.CharField(source='client.name', read_only=True, label='関連会社')
    manager__name = serializers.CharField(source='manager.name', read_only=True, label='案件責任者')
    contact__name = serializers.CharField(source='contact.name', read_only=True, label='案件連絡者')

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
