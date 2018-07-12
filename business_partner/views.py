from . import models, serializers
from utils.rest_base import BaseModelViewSet


class BusinessPartnerViewSet(BaseModelViewSet):
    queryset = models.BusinessPartner.objects.all()
    serializer_class = serializers.BusinessPartnerSerializer
