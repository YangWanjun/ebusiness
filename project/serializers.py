from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class ClientSerializer(BaseModelSerializer):

    class Meta:
        model = models.Client
        fields = '__all__'


class ProjectSerializer(BaseModelSerializer):
    client = ClientSerializer()
    client__name = serializers.CharField(source='client.name', read_only=True, label='関連会社')

    class Meta:
        model = models.Project
        fields = '__all__'
