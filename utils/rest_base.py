from collections import OrderedDict

from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import IntegerField
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import HyperlinkedModelSerializer


class BaseModelSerializer(HyperlinkedModelSerializer):

    # def get_columns(self):
    #     columns = []
    #     for name, field in self.get_fields().items():
    #         is_numeric = isinstance(field, IntegerField)
    #         columns.append({
    #             'id': name,
    #             'numeric': is_numeric,
    #             'disablePadding': not is_numeric,
    #             'label': field.label,
    #         })
    #     return columns
    pass


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
    list_display = ()
    list_display_links = ()
    filter_fields = ()

    def get_list_display(self):
        list_display = self.list_display
        if not list_display:
            list_display = ('id',)
        return list_display

    def get_list_display_links(self):
        return self.list_display_links

    def get_search_fields(self):
        return self.filter_fields

    def get_columns_definition(self, serializer):
        columns = []
        list_display = self.get_list_display()
        search_fields = self.get_search_fields()
        db_columns = [f.name for f in serializer.Meta.model._meta.fields]

        for name, field in serializer.get_fields().items():
            is_numeric = isinstance(field, IntegerField)
            columns.append({
                'id': name,
                'numeric': is_numeric,
                'disablePadding': False,
                'label': field.label,
                'visible': name in list_display,
                'searchable': name in search_fields,
                'sortable': name in db_columns
            })
        return columns

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            columns = self.get_columns_definition(serializer.child)
            return self.get_paginated_response(serializer.data, columns)

        serializer = self.get_serializer(queryset, many=True)
        columns = self.get_columns_definition(serializer.child)
        return Response(OrderedDict([
            ('columns', columns or []),
            ('results', serializer.data),
        ]))

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)
