import base64
from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from . import models, serializers
from utils.rest_base import BaseModelViewSet, BaseApiView


# Create your views here.
class ProjectStageViewSet(BaseModelViewSet):
    queryset = models.ProjectStage.objects.all()
    serializer_class = serializers.ProjectStageSerializer
    list_display = ('name',)


class BankAccountViewSet(BaseModelViewSet):
    queryset = models.BankAccount.objects.all()
    serializer_class = serializers.BankAccountSerializer


class FileDownloadApiView(BaseApiView):

    def get(self, request, *args, **kwargs):
        file_uuid = kwargs.get('uuid')
        attachment = get_object_or_404(models.Attachment, uuid=file_uuid)
        path = attachment.path.path
        with open(path, 'rb') as f:
            stream = base64.b64encode(f.read())
        return Response({
            'name': attachment.name,
            'blob': stream,
        })
