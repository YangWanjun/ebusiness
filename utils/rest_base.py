import datetime
import sys
from collections import OrderedDict

from django.utils import timezone

from rest_framework.fields import SkipField
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, \
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.serializers import IntegerField, DecimalField, DateTimeField, ChoiceField, \
    ModelSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.relations import PKOnlyObject
from rest_framework.response import Response


class BaseModelSerializer(ModelSerializer):

    def to_representation(self, instance):
        """
        Object instance -> Dict of primitive datatypes.
        """
        ret = OrderedDict()
        fields = self._readable_fields

        for field in fields:
            try:
                attribute = field.get_attribute(instance)
            except SkipField:
                continue

            # We skip `to_representation` for `None` values so that fields do
            # not have to explicitly deal with that case.
            #
            # For related fields with `use_pk_only_optimization` we need to
            # resolve the pk value.
            check_for_none = attribute.pk if isinstance(attribute, PKOnlyObject) else attribute
            if check_for_none is None:
                ret[field.field_name] = None
            elif isinstance(field, DateTimeField) and isinstance(attribute, datetime.datetime):
                # ローカルゾーンの時間に設定する。
                attribute = timezone.localtime(attribute)
                ret[field.field_name] = attribute.strftime('%Y-%m-%d %H:%M:%S')
            else:
                ret[field.field_name] = field.to_representation(attribute)

        return ret


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

        def get_index(lst, val):
            try:
                return lst.index(val)
            except ValueError:
                return sys.maxsize

        for name, field in serializer.get_fields().items():
            is_numeric = isinstance(field, (IntegerField, DecimalField))
            choices = field.choices if isinstance(field, ChoiceField) else dict()
            sort_field = get_sort_field(name, serializer)
            if self.get_list_display_links() and name in self.get_list_display_links():
                url_field = 'url'
            else:
                url_field = None
            columns.append({
                'id': name,
                'urlField': url_field,
                'numeric': is_numeric,
                'label': field.label,
                'visible': name in list_display,
                'choices': choices,
                'searchable': name in search_fields,
                'searchType': self.get_search_type(name),
                'sortable': True if sort_field else False,
                'sort_field': sort_field,
            })
        sort_list = [get_index(list_display, c.get('id')) for c in columns]
        return [x for x, _ in sorted(zip(columns, sort_list), key=lambda pair: pair[1])]

    def list(self, request, *args, **kwargs):
        schema = request.GET.get('schema', '1') or '1'
        if schema == '1':
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
        else:
            return super(BaseListModelMixin, self).list(request, *args, **kwargs)


class BaseRetrieveModelMixin(RetrieveModelMixin):

    def get_schema(self, serializer):
        columns = []
        for name, field in serializer.get_fields().items():
            is_numeric = isinstance(field, (IntegerField, DecimalField))
            choices = field.choices if isinstance(field, ChoiceField) else dict()
            columns.append({
                'id': name,
                'numeric': is_numeric,
                'label': field.label,
                'choices': choices,
            })
        return columns

    def retrieve(self, request, *args, **kwargs):
        if request.GET.get('schema') == '1':
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            columns = self.get_schema(serializer)
            data = serializer.data
            data.update({
                'columns': columns,
            })
            return Response(data)
        else:
            return super(BaseRetrieveModelMixin, self).retrieve(request, *args, **kwargs)


class BaseReadOnlyModelViewSet(BaseRetrieveModelMixin,
                               BaseListModelMixin,
                               GenericViewSet):
    pagination_class = MyLimitOffsetPagination

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)


class BaseModelViewSet(CreateModelMixin,
                       BaseRetrieveModelMixin,
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
