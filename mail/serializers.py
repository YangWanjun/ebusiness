from . import models
from utils.rest_base import BaseModelSerializer


class MailGroupSerializer(BaseModelSerializer):

    class Meta:
        model = models.MailGroup
        fields = '__all__'
