from . import models, serializers
from utils.django_base import BaseModelViewSet


class MemberViewSet(BaseModelViewSet):
    queryset = models.Member.objects.all()
    serializer_class = serializers.MemberSerializer
