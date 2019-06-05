import django_filters

from django.db import transaction

from rest_framework import status as rest_status
from rest_framework.response import Response

from . import models, serializers, biz
from member.biz import get_next_bp_employee_id
from member.serializers import MemberSerializer, OrganizationPeriodSerializer, SalespersonPeriodSerializer
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


class PartnerMembersApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_partner_members(kwargs.get('pk'))
        return {
            'count': len(data),
            'results': data,
        }

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        member_data = request.data.get('member')
        member_data['employee_id'] = get_next_bp_employee_id()
        organization_period = request.data.get('organization_period')
        salesperson_period = request.data.get('salesperson_period')
        bp_contract_data = request.data.get('bp_contract')
        member_serializer = MemberSerializer(data=member_data)
        errors = {}
        if member_serializer.is_valid():
            member = member_serializer.save()
            organization_period['member'] = member.pk
            salesperson_period['member'] = member.pk
            bp_contract_data['member'] = member.pk
            bp_contract_data['company'] = kwargs.get('pk')
            organization_period_serializer = OrganizationPeriodSerializer(data=organization_period)
            salesperson_period_serializer = SalespersonPeriodSerializer(data=salesperson_period)
            bp_contract_serializer = serializers.BpContractSerializer(data=bp_contract_data)
            if organization_period_serializer.is_valid() \
                    and salesperson_period_serializer.is_valid() \
                    and bp_contract_serializer.is_valid():
                organization_period_serializer.save()
                salesperson_period_serializer.save()
                bp_contract_serializer.save()
                return Response({'pk': member.pk})
            else:
                errors['organization_period'] = organization_period_serializer.errors
                errors['salesperson_period'] = salesperson_period_serializer.errors
                errors['bp_contract'] = bp_contract_serializer.errors
        else:
            errors['member'] = member_serializer.errors
        return Response(errors, status=rest_status.HTTP_400_BAD_REQUEST)


class BpContractViewSet(BaseModelViewSet):
    queryset = models.BpContract.objects.all()
    serializer_class = serializers.BpContractSerializer
    filter_fields = ('member',)


class PartnerMembersOrderStatusApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_partner_members_order_status(kwargs.get('pk'))
        return {
            'count': len(data),
            'results': data,
        }


class PartnerMemberOrdersApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_partner_member_orders(kwargs.get('member_id'))
        return {
            'count': len(data),
            'results': data,
        }
