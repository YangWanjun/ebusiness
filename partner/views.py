import django_filters

from . import models, serializers, biz
from utils.rest_base import BaseModelViewSet, BaseApiView


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


class PartnerListApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_partner_list()
        return {
            'count': len(data),
            'results': data,
        }


class PartnerMemberViewSet(BaseModelViewSet):
    queryset = models.PartnerMember.objects.all()
    serializer_class = serializers.PartnerMemberSerializer
    filter_fields = ('company',)


class PartnerPayNotifyRecipientViewSet(BaseModelViewSet):
    queryset = models.PartnerPayNotifyRecipient.objects.all()
    serializer_class = serializers.PartnerPayNotifyRecipientSerializer
    filter_fields = ('company',)
