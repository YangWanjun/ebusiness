import operator
import django_filters

from functools import reduce

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from rest_framework import status as rest_status
from rest_framework.response import Response

from . import models, serializers, biz
from master.models import Company, BankAccount, Attachment
from utils import constants, file_gen, common
from utils.rest_base import BaseModelViewSet, BaseModelSchemaView, BaseApiView


# Create your views here.
class CustomerViewSet(BaseModelViewSet):
    queryset = models.Customer.objects.all()
    serializer_class = serializers.CustomerSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)

    def get_queryset(self):
        search = self.request.GET.get('search')
        if not search:
            return self.queryset
        else:
            return self.queryset.filter(name__icontains=search)


class CustomerMemberViewSet(BaseModelViewSet):
    queryset = models.CustomerMember.objects.all()
    serializer_class = serializers.CustomerMemberSerializer
    list_display = ('name', 'customer__name', 'email')

    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = self.queryset
        if not search:
            return queryset
        else:
            for bit in search.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in ('name__icontains', 'customer__name__icontains')]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            return queryset


class VProjectFilter(django_filters.FilterSet):

   class Meta:
        model = models.VProject
        fields = {
            'name': ['icontains'],
            'customer_name': ['icontains'],
            'business_type': ['iexact'],
            'status': ['iexact'],
        }


class ProjectViewSet(BaseModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    choice_classes = {
        'status': constants.DICT_PROJECT_STATUS_CLASS,
    }


class VProjectViewSet(BaseModelViewSet):
    queryset = models.VProject.objects.all()
    serializer_class = serializers.VProjectSerializer
    list_display = (
        'name', 'customer_name', 'business_type', 'salesperson_name', 'member_name',
        'start_date', 'end_date', 'updated_dt', 'status'
    )
    list_display_links = ('name',)
    filter_fields = ('name', 'customer_name', 'business_type', 'status')
    filter_class = VProjectFilter
    choice_classes = {
        'status': constants.DICT_PROJECT_STATUS_CLASS,
    }


class ProjectMemberSchemaView(BaseModelSchemaView):

    @classmethod
    def get_extra_schema(cls):
        return {
            'member': {
                'search_url': '/api/member/search?schema=1'
            }
        }


class ProjectMemberViewSet(BaseModelViewSet):
    queryset = models.ProjectMember.objects.all()
    serializer_class = serializers.ProjectMemberSerializer
    schema_class = ProjectMemberSchemaView
    list_display = (
        'member_name', 'start_date', 'end_date',
        'price', 'min_hours', 'max_hours', 'plus_per_hour', 'minus_per_hour', 'hourly_pay',
        'contract_type', 'status',
    )
    pagination_class = None
    choice_classes = {
        'status': constants.DICT_PROJECT_MEMBER_STATUS_CLASS,
    }

    def get_queryset(self):
        project_id = self.request.GET.get('project')
        if not project_id:
            return self.queryset.none()
        else:
            return self.queryset.filter(project__pk=project_id)


class ProjectAttendanceList(BaseApiView):

    def get_context_data(self, **kwargs):
        project_id = kwargs.get('pk')
        attendance_list = biz.get_project_attendance_list(project_id)
        return {
            'count': len(attendance_list),
            'results': attendance_list
        }


class ProjectAttendanceView(BaseApiView):

    def get_context_data(self, **kwargs):
        project_id = kwargs.get('pk')
        year = kwargs.get('year')
        month = kwargs.get('month')
        attendance_list = biz.get_project_attendance(project_id, year, month)
        return {
            'count': len(attendance_list),
            'results': attendance_list
        }


class MemberAttendanceViewSet(BaseModelViewSet):
    queryset = models.MemberAttendance.objects.all()
    serializer_class = serializers.MemberAttendanceSerializer


class ProjectOrderListView(BaseApiView):

    def get_context_data(self, **kwargs):
        project_id = kwargs.get('pk')
        order_list = biz.get_project_order_list(project_id)
        return {
            'count': len(order_list),
            'results': order_list
        }


class CustomerOrderViewSet(BaseModelViewSet):
    queryset = models.CustomerOrder.objects.all()
    serializer_class = serializers.CustomerOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        data['projects'] = biz.get_project_choice(data['projects'])
        headers = self.get_success_headers(data)
        return Response(data, status=rest_status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        data = serializer.data
        data['projects'] = biz.get_project_choice(data['projects'])
        return Response(data)


class SearchProjectView(BaseApiView):

    def get_columns(self):
        return [
            {
                "name": "name",
                "type": "string",
                "label": "案件名称",
                "visible": True,
            },
            {
                "name": "customer__name",
                "type": "string",
                "label": "関連会社",
                "visible": True,
            },
            {
                "name": "organization__name",
                "type": "string",
                "label": "所属部署",
                "visible": True,
            },
            {
                "name": "start_date",
                "type": "date",
                "label": "開始日",
            },
            {
                "name": "end_date",
                "type": "date",
                "label": "終了日",
            },
        ]

    def get_context_data(self, **kwargs):
        search = self.request.GET.get('search', None)
        queryset = biz.search_project(search)
        projects = serializers.ProjectSerializer(queryset, many=True)
        return {
            'count': queryset.count(),
            'results': projects.data,
        }


class ProjectRequestDetailApiView(BaseApiView):
    template_name = 'project/project_request.html'

    def get_context_data(self, **kwargs):
        request_no = kwargs.get('request_no')
        project_request = models.ProjectRequest.objects.get(request_no=request_no)
        heading = project_request.projectrequestheading
        details = list(project_request.projectrequestdetail_set.all())
        if len(details) < 20:
            details.extend([None] * (20 - len(details)))
        data = {
            'project_request': project_request,
            'heading': heading,
            'details': details,
        }
        html = render_to_string(self.template_name, {'data': data})
        return {'html': html}


class ProjectRequestCreateApiView(BaseApiView):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        company = Company.get_company()
        project = get_object_or_404(models.Project, pk=kwargs.get('project_id'))
        customer_order = get_object_or_404(models.CustomerOrder, pk=kwargs.get('order_id'))
        year = kwargs.get('year')
        month = kwargs.get('month')
        initial = {
            'bank_account': get_object_or_404(BankAccount, pk=request.data.get('bank_account_id')),
            'contract_name': request.data.get('contract_name'),
            'order_no': request.data.get('order_no'),
        }
        project_request = project.get_project_request(year, month, customer_order)
        request_data = biz.generate_request_data(company, project, customer_order, year, month, initial)
        heading = request_data.get('heading')
        byte_file = file_gen.generate_request(request_data, project_request.request_no)
        project_request.request_name = heading.get('CONTRACT_NAME')
        project_request.amount = heading['ITEM_AMOUNT_ALL']
        project_request.turnover_amount = heading.get('ITEM_AMOUNT_ATTENDANCE')
        project_request.tax_amount = heading.get('ITEM_AMOUNT_ATTENDANCE_TAX')
        project_request.expenses_amount = heading.get('ITEM_AMOUNT_EXPENSES')
        project_request.created_user = request.user
        project_request.updated_user = request.user
        project_request.save(other_data=request_data)
        filename = common.get_request_filename(project_request.request_no, heading.get('CONTRACT_NAME'))
        attachment = Attachment.save_from_bytes(
            project_request,
            byte_file,
            filename,
            existed_file=project_request.filename
        )
        project_request.filename = attachment.uuid
        project_request.save(update_fields=('filename',))
        data = serializers.CustomerOrderSerializer(customer_order).data
        data['projects'] = biz.get_project_choice(data['projects'])
        data['request_no'] = project_request.request_no
        data['request_detail_url'] = '/project/{pk}/request/{request_no}'.format(
            pk=project.pk,
            request_no=project_request.request_no,
        )
        data['uuid'] = project_request.filename
        return Response(data)
