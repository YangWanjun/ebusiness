from . import models
from utils.django_base import BaseModelSerializer


class MemberSerializer(BaseModelSerializer):

    class Meta:
        model = models.Member
        fields = '__all__'
