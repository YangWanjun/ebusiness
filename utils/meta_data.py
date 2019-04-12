from collections import OrderedDict

from django.db import models

from rest_framework import serializers
from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from utils import common


class BaseSimpleMetadata(SimpleMetadata):
    schema_object = None
    serializer = None

    def determine_metadata(self, request, view):
        if view.schema_class:
            self.schema_object = view.schema_class(view)
        metadata = OrderedDict()
        # metadata['name'] = view.get_view_name()
        # metadata['description'] = view.get_view_description()
        # metadata['renders'] = [renderer.media_type for renderer in view.renderer_classes]
        # metadata['parses'] = [parser.media_type for parser in view.parser_classes]
        if hasattr(view, 'get_serializer'):
            self.serializer = view.get_serializer()
            columns = self.get_serializer_info(self.serializer, view)
            metadata['columns'] = columns
            metadata['fieldsets'] = self.schema_object.get_fieldsets()
            if not metadata['fieldsets']:
                if view.serializer_class.Meta.fields == '__all__':
                    model = view.serializer_class.Meta.model
                    model_fields = [field.name for field in model._meta.fields]
                    model_fields.extend([
                        field_name for field_name in self.serializer.fields.keys()
                        if field_name not in model_fields
                    ])
                    sort_list = []
                    for i, col in enumerate(columns):
                        try:
                            sort_list.append(model_fields.index(col['name']))
                        except ValueError:
                            sort_list.append(10000 + i)
                    metadata['columns'] = [c for c, _ in sorted(zip(columns, sort_list), key=lambda pair: pair[1])]
        return metadata

    def get_serializer_info(self, serializer, view=None):
        """
        Given an instance of a serializer, return a dictionary of metadata
        about its fields.
        """
        if hasattr(serializer, 'child'):
            # If this is a `ListSerializer` then we want to examine the
            # underlying child serializer instance instead.
            serializer = serializer.child
        return list([
            self.get_field_info(field, view)
            for field in serializer.fields.values()
            if not isinstance(field, serializers.HiddenField)
        ])

    def get_field_info(self, field, view=None):
        field_info = super(BaseSimpleMetadata, self).get_field_info(field)
        field_info['name'] = field.field_name
        field_type = self.test_field_type(field)
        if field_type:
            field_info['type'] = field_type
        if view:
            field_info['visible'] = field.field_name in view.get_list_display()
        else:
            field_info['visible'] = False
        if view and view.get_list_display_links() and field.field_name in view.get_list_display_links():
            field_info['url_field'] = 'url'
        else:
            field_info['url_field'] = None
        # 並び替え
        sort_field = self.get_sort_field(field)
        if sort_field:
            field_info['sortable'] = True
            field_info['sort_field'] = sort_field
        # 検索
        if self.is_searchable(field, view):
            field_info['searchable'] = True
            field_info['search_type'] = self.get_search_type(field, view)
        if self.schema_object and self.schema_object.get_extra_schema():
            extra = self.schema_object.get_extra_schema().get(field.field_name, None)
            if extra and isinstance(extra, dict):
                field_info.update(extra)
        return field_info

    def test_field_type(self, field):
        if isinstance(field, serializers.SerializerMethodField):
            method = getattr(self.serializer, field.method_name)
            if hasattr(method, 'field_type'):
                return method.field_type
            else:
                return 'string'
        else:
            return None

    def get_sort_field(self, field):
        """並び替え時の並び替え項目名を取得する

        :param field:
        :return:
        """
        if field.field_name in [f.name for f in self.serializer.Meta.model._meta.fields]:
            # 項目がＤＢ項目の場合、並び替え可
            return field.field_name
        elif hasattr(self.serializer, 'get_' + field.field_name):
            method = getattr(self.serializer, 'get_' + field.field_name)
            if hasattr(method, 'sort_field'):
                return getattr(method, 'sort_field')
        return None

    def is_searchable(self, field, view=None):
        """検索できるかどうか

        :param field:
        :param view:
        :return:
        """
        return (field.field_name in view.filter_fields) if view else False

    def get_search_type(self, field, view=None):
        if view.filter_class:
            fields = view.filter_class.Meta.fields
            lookups = fields.get(field.field_name)
            return lookups[0] if lookups else None
        else:
            return None


class BaseModelMetadata(SimpleMetadata):

    label_lookup = ClassLookupDict({
        models.ForeignKey: 'field',
        models.BooleanField: 'boolean',
        models.NullBooleanField: 'boolean',
        models.CharField: 'string',
        models.UUIDField: 'string',
        models.URLField: 'url',
        models.EmailField: 'email',
        # models.RegexField: 'regex',
        models.SlugField: 'slug',
        models.AutoField: 'integer',
        models.IntegerField: 'integer',
        models.PositiveIntegerField: 'integer',
        models.PositiveSmallIntegerField: 'integer',
        models.SmallIntegerField: 'integer',
        models.BigIntegerField: 'integer',
        models.FloatField: 'float',
        models.DecimalField: 'decimal',
        models.DateField: 'date',
        models.DateTimeField: 'datetime',
        models.TimeField: 'time',
        # models.ChoiceField: 'choice',
        # models.MultipleChoiceField: 'multiple choice',
        models.FileField: 'file upload',
        models.ImageField: 'image upload',
        # models.ListField: 'list',
        # models.DictField: 'nested object',
        # models.Serializer: 'nested object',
    })

    def determine_metadata(self, request, view):
        metadata = OrderedDict()
        metadata['columns'] = self.get_model_info(view.model_class, view)
        return metadata

    def get_model_info(self, model, view=None):
        if not model:
            return list()
        return [
            self.get_field_info(field, view) for field in model._meta.fields
        ]

    def get_field_info(self, field, view=None):
        """Modelの項目定義を取得する

        :param field:
        :return:
        """
        field_info = OrderedDict()
        field_info['name'] = field.name
        if field.choices:
            field_info['type'] = 'choice'
            field_info['choices'] = common.choices_to_dict_list(field.choices)
        else:
            field_info['type'] = self.label_lookup[field]
        field_info['required'] = field.blank
        field_info['read_only'] = field.editable
        field_info['label'] = field.verbose_name
        if view:
            field_info['visible'] = field.name in view.get_list_display()
        else:
            field_info['visible'] = False
        field_info['searchable'] = False
        return field_info
