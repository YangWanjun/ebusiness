from django.db import models

from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer


class DefaultManager(models.Manager):

    def __init__(self, *args, **kwargs):
        super(DefaultManager, self).__init__()
        self.args = args
        self.kwargs = kwargs

    def get_queryset(self):
        return super(DefaultManager, self).get_queryset().filter(*self.args, **self.kwargs)


class BaseModel(models.Model):
    created_dt = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    objects = DefaultManager()

    class Meta:
        abstract = True


class BaseModelSerializer(ModelSerializer):
    pass


class BaseModelViewSet(ModelViewSet):
    pass
