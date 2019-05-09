from . import models
from utils.rest_base import BaseModelSerializer


class ProjectStageSerializer(BaseModelSerializer):

    class Meta:
        model = models.ProjectStage
        fields = '__all__'
