import django_filters

from . import models, serializers
from utils.rest_base import BaseModelViewSet


class PartnerFilter(django_filters.FilterSet):

   class Meta:
        model = models.Partner
        fields = {
            'name': ['icontains'],
            'president': ['icontains'],
        }


class PartnerViewSet(BaseModelViewSet):
    queryset = models.Partner.objects.all()
    serializer_class = serializers.PartnerSerializer
    list_display = ('name', 'president', 'address', 'tel')
    filter_fields = ('name', 'president')
    filter_class = PartnerFilter
