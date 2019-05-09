from . import models, serializers
from utils.rest_base import BaseModelViewSet


# Create your views here.
class ProjectStageViewSet(BaseModelViewSet):
    queryset = models.ProjectStage.objects.all()
    serializer_class = serializers.ProjectStageSerializer
    list_display = ('name',)
