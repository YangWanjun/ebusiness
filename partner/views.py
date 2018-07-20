from . import models, serializers
from utils.rest_base import BaseModelViewSet


class PartnerViewSet(BaseModelViewSet):
    queryset = models.Partner.objects.all()
    serializer_class = serializers.PartnerSerializer
    list_display = ('name', 'president', 'address', 'tel')
    search_fields = ('name', 'president')
