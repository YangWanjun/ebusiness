from . import models, serializers
from utils.rest_base import BaseModelViewSet


# Create your views here.
class ClientViewSet(BaseModelViewSet):
    queryset = models.Client.objects.all()
    serializer_class = serializers.ClientSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)


class ProjectViewSet(BaseModelViewSet):
    queryset = models.Project.objects.all()
    serializer_class = serializers.ProjectSerializer
    list_display = ('name',)
    list_display_links = ('name',)
    filter_fields = ('name',)
