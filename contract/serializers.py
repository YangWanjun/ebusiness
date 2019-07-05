from . import models
from utils.rest_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):

    class Meta:
        model = models.VMember
        fields = '__all__'
