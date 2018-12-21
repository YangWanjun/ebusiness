from . import models
from utils.rest_base import BaseModelSerializer


class TurnoverMonthlySerializer(BaseModelSerializer):

    class Meta:
        model = models.TurnoverMonthly
        fields = '__all__'
