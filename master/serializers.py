from . import models
from utils.rest_base import BaseModelSerializer


class ProjectStageSerializer(BaseModelSerializer):

    class Meta:
        model = models.ProjectStage
        fields = '__all__'


class BankSerializer(BaseModelSerializer):

    class Meta:
        model = models.Bank
        fields = '__all__'


class BankAccountSerializer(BaseModelSerializer):

    class Meta:
        model = models.BankAccount
        fields = '__all__'
