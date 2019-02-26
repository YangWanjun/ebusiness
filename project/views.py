import django_filters

from . import models, serializers
from utils.rest_base import BaseModelViewSet


# Create your views here.
class ClientViewSet(BaseModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)


class ProjectFilter(django_filters.FilterSet):

   class Meta:
        model = models.Project
        fields = {
            'name': ['icontains'],
            'client__name': ['icontains'],
        }


class ProjectViewSet(BaseModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    list_display = ('name', 'client__name', 'business_type', 'start_date', 'end_date', 'updated_dt')
    list_display_links = ('name',)
    filter_fields = ('name', 'client__name', 'business_type')
    filter_class = ProjectFilter
