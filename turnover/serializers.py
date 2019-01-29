from . import models
from utils.rest_base import BaseModelSerializer


class TurnoverMonthlySerializer(BaseModelSerializer):

    class Meta:
        model = models.TurnoverMonthly
        fields = '__all__'


class TurnoverYearlySerializer(BaseModelSerializer):

    class Meta:
        model = models.TurnoverYearly
        fields = '__all__'
