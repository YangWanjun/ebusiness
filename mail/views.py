from rest_framework.decorators import action
from rest_framework.response import Response

from . import models, serializers, biz
from utils.rest_base import BaseModelViewSet


# Create your views here.
class MailGroupViewSet(BaseModelViewSet):
    queryset = models.MailGroup.objects.all()
    serializer_class = serializers.MailGroupSerializer

    @action(methods=['post'], detail=False)
    def send(self, request, *args, **kwargs):
        data = biz.send_mail(request.data, request.user)
        if data:
            return Response(data)
        else:
            return Response({'detail': 'success'})
