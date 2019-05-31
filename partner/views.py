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


class PartnerEmployeeViewSet(BaseModelViewSet):
    queryset = models.PartnerEmployee.objects.all()
    serializer_class = serializers.PartnerEmployeeSerializer
    filter_fields = ('company',)


class PartnerPayNotifyRecipientViewSet(BaseModelViewSet):
    queryset = models.PartnerPayNotifyRecipient.objects.all()
    serializer_class = serializers.PartnerPayNotifyRecipientSerializer
    filter_fields = ('company',)


class PartnerEmployeeChoiceApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        return biz.get_partner_employee_choices(kwargs.get('pk'))


class PartnerBankAccountViewSet(BaseModelViewSet):
    queryset = models.PartnerBankAccount.objects.all()
    serializer_class = serializers.PartnerBankAccountSerializer
    filter_fields = ('company',)


class PartnerMonthlyStatusApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_partner_monthly_status(kwargs.get('pk'))
        return {
            'count': len(data),
            'results': data,
        }
