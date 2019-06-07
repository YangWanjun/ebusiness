import datetime
import django_filters

from django.db import transaction
from django.template.loader import render_to_string

from rest_framework import status as rest_status
from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers, biz
from master.models import Company, Attachment
from member.biz import get_next_bp_employee_id, get_member_salesperson_by_month
from member.serializers import MemberSerializer, OrganizationPeriodSerializer, SalespersonPeriodSerializer
from project.models import ProjectMember
from utils import file_gen, common
from utils.django_base import BaseTemplateViewWithoutLogin
from utils.rest_base import BaseModelViewSet, BaseApiView, BaseReadOnlyModelViewSet


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


class BpMemberOrderViewSet(BaseReadOnlyModelViewSet):
    queryset = models.BpMemberOrder.objects.all()
    serializer_class = serializers.BpMemberOrderSerializer

    @action(methods=['get'], detail=True)
    def mail(self, *args, **kwargs):
        mail_data = self.get_object().get_mail_data()
        return Response(mail_data)


class MemberOrderDetailApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        order = models.BpMemberOrder.objects.get(pk=kwargs.get('pk'))
        heading = order.bpmemberorderheading
        data = {
            'order': order,
            'heading': heading,
        }
        return {'html': [
            render_to_string('partner/member_order.html', {'data': data}),
            render_to_string('partner/member_order_request.html', {'data': data})
        ]}


class BpMemberOrderCreateApiView(BaseApiView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        company = Company.get_company()
        partner = models.Partner.objects.get(pk=kwargs.get('pk'))
        project_member = ProjectMember.objects.get(pk=kwargs.get('project_member_id'))
        year = request.data.get('year')
        month = request.data.get('month')
        first_day = common.get_first_day_from_ym(year + month)
        last_day = common.get_last_day_by_month(first_day)
        end_date = last_day if last_day <= project_member.end_date else project_member.end_date
        publish_date = datetime.datetime.strptime(request.data.get('publish_date'), '%Y-%m-%d')
        end_year = request.data.get('end_year')
        end_month = request.data.get('end_month')
        salesperson = get_member_salesperson_by_month(project_member.member, end_date)
        order = models.BpMemberOrder.get_next_bp_order(
            partner, project_member, year, month, publish_date, end_year, end_month, salesperson
        )
        order_data = biz.generate_partner_order_data(
            company, partner, project_member,
            order.order_no,
            year,
            month,
            publish_date,
            end_year,
            end_month,
        )
        if not order.pk:
            order.created_user = request.user
        order.updated_user = request.user
        order.save(other_data=order_data)
        filename, filename_request = common.get_order_file_path(order.order_no, project_member.member.full_name)
        # 注文書
        html = render_to_string('partner/member_order.html', {'data': order_data})
        byte_file = file_gen.generate_report_pdf_binary(html)
        attachment = Attachment.save_from_bytes(
            order,
            byte_file,
            filename,
            existed_file=order.filename
        )
        order.filename = attachment.uuid
        # 注文請書
        html = render_to_string('partner/member_order_request.html', {'data': order_data})
        byte_file = file_gen.generate_report_pdf_binary(html)
        attachment = Attachment.save_from_bytes(
            order,
            byte_file,
            filename_request,
            existed_file=order.filename_request
        )
        order.filename_request = attachment.uuid
        order.save(update_fields=('filename', 'filename_request'))
        return Response(serializers.BpMemberOrderDisplaySerializer(order).data)


class PreviewPdfView(BaseTemplateViewWithoutLogin):
    template_name = 'partner/member_order_request.html'

    def get_context_data(self, **kwargs):
        order = models.BpMemberOrder.objects.get(pk=4446)
        heading = order.bpmemberorderheading
        data = {
            'order': order,
            'heading': heading,
        }
        return {'data': data}


class BpLumpContractViewSet(BaseModelViewSet):
    queryset = models.BpLumpContract.objects.filter(is_deleted=False)
    serializer_class = serializers.BpLumpContractSerializer
    filter_fields = ('company',)


class PartnerLumpContractApiView(BaseApiView):

    def get_context_data(self, pk, **kwargs):
        data = biz.get_partner_lump_contracts(pk)
        return {
            'count': len(data),
            'results': data,
        }
