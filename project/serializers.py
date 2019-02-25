from . import models
from utils.rest_base import BaseModelSerializer


class ClientSerializer(BaseModelSerializer):

    class Meta:
        model = models.Client
        fields = '__all__'


class ProjectSerializer(BaseModelSerializer):
    client = ClientSerializer()

    class Meta:
        model = models.Project
        fields = '__all__'
