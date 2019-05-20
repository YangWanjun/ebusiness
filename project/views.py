import operator
import django_filters

from functools import reduce

from django.db.models import Q

from rest_framework import status as rest_status
from rest_framework.response import Response

from . import models, serializers, biz
from utils import constants
from utils.rest_base import BaseModelViewSet, BaseModelSchemaView, BaseApiView


# Create your views here.
class ClientViewSet(BaseModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)

    def get_queryset(self):
        search = self.request.GET.get('search')
        if not search:
            return self.queryset
        else:
            return self.queryset.filter(name__icontains=search)


class ClientMemberViewSet(BaseModelViewSet):
    queryset = models.ClientMember.objects.all()
    serializer_class = serializers.ClientMemberSerializer
    list_display = ('name', 'client__name', 'email')

    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = self.queryset
        if not search:
            return queryset
        else:
            for bit in search.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in ('name__icontains', 'client__name__icontains')]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            return queryset


class VProjectFilter(django_filters.FilterSet):

   class Meta:
        model = models.VProject
        fields = {
            'name': ['icontains'],
            'client_name': ['icontains'],
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
        'name', 'client_name', 'business_type', 'salesperson_name', 'member_name',
        'start_date', 'end_date', 'updated_dt', 'status'
    )
    list_display_links = ('name',)
    filter_fields = ('name', 'client_name', 'business_type', 'status')
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


class ClientOrderViewSet(BaseModelViewSet):
    queryset = models.ClientOrder.objects.all()
    serializer_class = serializers.ClientOrderSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = serializer.data
        project_list = []
        for project in models.Project.objects.filter(pk__in=data['projects']):
            project_list.append({
                'value': project.pk,
                'display_name': project.name,
            })
        data['projects'] = project_list
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
        project_list = []
        for project in models.Project.objects.filter(pk__in=data['projects']):
            project_list.append({
                'value': project.pk,
                'display_name': project.name,
            })
        data['projects'] = project_list
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
                "name": "client__name",
                "type": "string",
                "label": "関連会社",
                "visible": True,
            },
            {
                "name": "organization__name",
                "type": "string",
                "label": "所属部署",
                "visible": True,
            }
        ]

    def get_context_data(self, **kwargs):
        search = self.request.GET.get('search', None)
        queryset = biz.search_project(search)
        projects = serializers.ProjectSerializer(queryset, many=True)
        return {
            'count': queryset.count(),
            'results': projects.data,
        }
