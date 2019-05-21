import datetime
from collections import OrderedDict

from django.db.models.deletion import ProtectedError
from django.utils import timezone

from rest_framework import status as rest_status
from rest_framework.fields import SkipField
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, \
    RetrieveModelMixin, CreateModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.serializers import DateTimeField, ModelSerializer
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.relations import PKOnlyObject
from rest_framework.response import Response

from utils import constants
from utils.meta_data import BaseModelMetadata


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
    choice_classes = {}
    row_classes = {}

    def get_list_display(self):
        list_display = self.list_display
        if not list_display:
            list_display = ('id',)
        return list_display

    def get_list_display_links(self):
        return self.list_display_links

    def list(self, request, *args, **kwargs):
        schema = request.GET.get('schema', '1') or '1'
        if schema == '1':
            queryset = self.filter_queryset(self.get_queryset())
            data = self.metadata_class().determine_metadata(request, self)
            columns = data.get('columns', list()) if data else list()
            fieldsets = data.get('fieldsets', list()) if data else list()

            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data, columns)

            serializer = self.get_serializer(queryset, many=True)
            return Response(OrderedDict([
                ('count', queryset.count()),
                ('columns', columns),
                ('fieldsets', fieldsets),
                ('results', serializer.data),
            ]))
        else:
            return super(BaseListModelMixin, self).list(request, *args, **kwargs)


class BaseRetrieveModelMixin(RetrieveModelMixin):
    choice_classes = {}


class BaseDestroyModelMixin(DestroyModelMixin):

    def destroy(self, request, *args, **kwargs):
        try:
            return super(BaseDestroyModelMixin, self).destroy(request, *args, **kwargs)
        except ProtectedError as ex:
            if hasattr(ex, 'protected_objects'):
                message = constants.ERROR_DELETE_PROTECTED.format(
                    name=ex.protected_objects.model._meta.verbose_name
                )
            else:
                message = constants.ERROR_DELETE_PROTECTED.format('データ')
            return Response({'detail': message}, status=rest_status.HTTP_400_BAD_REQUEST)


class BaseModelSchemaView(object):
    fieldsets = ()

    def __init__(self, view):
        self.view = view
        self.serializer = None
        if hasattr(view, 'get_serializer'):
            self.serializer = view.get_serializer()

    def get_fieldsets(self):
        if self.fieldsets:
            return self.fieldsets
        # elif self.view.serializer_class.Meta.fields == '__all__':
        #     model = self.view.serializer_class.Meta.model
        #     model_fields = [field.name for field in model._meta.fields]
        #     if self.serializer:
        #         model_fields.extend([
        #             field_name for field_name in self.serializer.fields.keys()
        #             if field_name not in model_fields
        #         ])
        #     return model_fields
        else:
            return tuple()

    @classmethod
    def get_extra_schema(cls):
        pass


class BaseReadOnlyModelViewSet(BaseRetrieveModelMixin,
                               BaseListModelMixin,
                               GenericViewSet):
    pagination_class = MyLimitOffsetPagination
    schema_class = BaseModelSchemaView

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)


class BaseModelViewSet(CreateModelMixin,
                       BaseRetrieveModelMixin,
                       UpdateModelMixin,
                       BaseDestroyModelMixin,
                       BaseListModelMixin,
                       GenericViewSet):
    pagination_class = MyLimitOffsetPagination
    schema_class = BaseModelSchemaView

    def get_paginated_response(self, data, columns=None):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data, columns)


class BaseApiView(APIView):
    metadata_class = BaseModelMetadata
    model_class = None

    def get_list_display(self):
        return []

    def get_context_data(self, **kwargs):
        pass

    def get_columns(self):
        return []

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.GET.get('schema', None) == '1':
            if self.get_columns():
                columns = {'columns': self.get_columns()}
            else:
                columns = self.metadata_class().determine_metadata(request, self)
            context.update(columns)
        return Response(context)

    def post(self, request, *args, **kwargs):
        pass
