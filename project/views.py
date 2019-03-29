import django_filters

from . import models, serializers
from utils import constants
from utils.rest_base import BaseModelViewSet, BaseModelSchemaView


# Create your views here.
class ClientViewSet(BaseModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)


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
                'search_url': ''
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
