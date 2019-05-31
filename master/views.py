import os
import base64
import operator
from functools import reduce

from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response

from . import models, serializers
from utils import constants
from utils.errors import CustomException
from utils.rest_base import BaseModelViewSet, BaseApiView


# Create your views here.
class ProjectStageViewSet(BaseModelViewSet):
    queryset = models.ProjectStage.objects.all()
    serializer_class = serializers.ProjectStageSerializer
    list_display = ('name',)


class BankViewSet(BaseModelViewSet):
    queryset = models.Bank.objects.all()
    serializer_class = serializers.BankSerializer
    list_display = ('code', 'name', 'kana')

    def get_queryset(self):
        search = self.request.GET.get('search')
        queryset = self.queryset
        if not search:
            return queryset
        else:
            for bit in search.split():
                or_queries = [Q(**{orm_lookup: bit}) for orm_lookup in ('code', 'name__icontains', 'kana__icontains')]
                queryset = queryset.filter(reduce(operator.or_, or_queries))
            return queryset


class BankAccountViewSet(BaseModelViewSet):
    queryset = models.BankAccount.objects.all()
    serializer_class = serializers.BankAccountSerializer


class FileDownloadApiView(BaseApiView):

    def get(self, request, *args, **kwargs):
        file_uuid = kwargs.get('uuid')
        attachment = get_object_or_404(models.Attachment, uuid=file_uuid)
        path = attachment.path.path
        if os.path.exists(path):
            with open(path, 'rb') as f:
                stream = base64.b64encode(f.read())
            return Response({
                'name': attachment.name,
                'blob': stream,
            })
        else:
            raise CustomException(constants.ERROR_FILE_NOT_FOUND)
