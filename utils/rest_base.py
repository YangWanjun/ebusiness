from collections import OrderedDict

from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, \
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.serializers import IntegerField, DecimalField
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer


class BaseModelSerializer(ModelSerializer):

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


class BaseListModelMixin(ListModelMixin):
    list_display = ()
    list_display_links = ()
    filter_fields = ()
    filter_class = None

    def get_list_display(self):
        list_display = self.list_display
        if not list_display:
            list_display = ('id',)
        return list_display

    def get_list_display_links(self):
        return self.list_display_links

    def get_search_fields(self):
        return self.filter_fields

    def get_search_type(self, field_name):
        if self.filter_class:
            fields = self.filter_class.Meta.fields
            lookups = fields.get(field_name)
            return lookups[0] if lookups else None
        else:
            return None

    def get_columns_definition(self, serializer):
        columns = []
        list_display = self.get_list_display()
        search_fields = self.get_search_fields()
        db_columns = [f.name for f in serializer.Meta.model._meta.fields]

        # ソート項目を取得する
        def get_sort_field(n, s):
            if n in db_columns:
                return n
            elif hasattr(s, 'get_' + n):
                method = getattr(s, 'get_' + n)
                if hasattr(method, 'sort_field'):
                    return getattr(method, 'sort_field')
            return None

        for name, field in serializer.get_fields().items():
            is_numeric = isinstance(field, (IntegerField, DecimalField))
            sort_field = get_sort_field(name, serializer)
            if self.get_list_display_links() and name in self.get_list_display_links():
                url_field = 'url'
            else:
                url_field = None
            columns.append({
                'id': name,
                'urlField': url_field,
                'numeric': is_numeric,
                'disablePadding': False,
                'label': field.label,
                'visible': name in list_display,
                'searchable': name in search_fields,
                'searchType': self.get_search_type(name),
                'sortable': True if sort_field else False,
                'sort_field': sort_field,
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


class BaseReadOnlyModelViewSet(RetrieveModelMixin,
                               BaseListModelMixin,
                               GenericViewSet):
    pagination_class = MyLimitOffsetPagination

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)


class BaseModelViewSet(CreateModelMixin,
                       RetrieveModelMixin,
                       UpdateModelMixin,
                       DestroyModelMixin,
                       BaseListModelMixin,
                       GenericViewSet):
    pagination_class = MyLimitOffsetPagination

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)


class BaseApiView(APIView):
    pass
