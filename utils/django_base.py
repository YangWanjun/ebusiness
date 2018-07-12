from collections import OrderedDict

from django.db import models

from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import IntegerField
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
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

    def get_columns(self):
        columns = []
        for name, field in self.get_fields().items():
            is_numeric = isinstance(field, IntegerField)
            columns.append({
                'id': name,
                'numeric': is_numeric,
                'disablePadding': not is_numeric,
                'label': field.label,
            })
        return columns


class MyLimitOffsetPagination(LimitOffsetPagination):

    def get_paginated_response(self, data, columns=None):
        return Response(OrderedDict([
            ('count', self.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('columns', columns or []),
            ('results', data),
        ]))


class BaseModelViewSet(ModelViewSet):
    pagination_class = MyLimitOffsetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            columns = serializer.child.get_columns()
            return self.get_paginated_response(serializer.data, columns)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)
