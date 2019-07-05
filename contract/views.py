from . import models, serializers
from utils.rest_base import BaseReadOnlyModelViewSet


# Create your views here.
class VMemberViewSet(BaseReadOnlyModelViewSet):
    queryset = models.VMember.objects.all()
    serializer_class = serializers.MemberSerializer
    pagination_class = None
