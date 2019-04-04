from collections import OrderedDict

from django.db import models

from rest_framework.metadata import SimpleMetadata
from rest_framework.utils.field_mapping import ClassLookupDict

from utils import common


class BaseSimpleMetadata(SimpleMetadata):
    schema_class = None

    def determine_metadata(self, request, view):
        self.schema_class = view.schema_class
        metadata = OrderedDict()
        metadata['name'] = view.get_view_name()
        metadata['description'] = view.get_view_description()
        metadata['renders'] = [renderer.media_type for renderer in view.renderer_classes]
        metadata['parses'] = [parser.media_type for parser in view.parser_classes]
        if hasattr(view, 'get_serializer'):
            actions = self.determine_actions(request, view)
            if actions:
                metadata['actions'] = actions
        return metadata

    def get_field_info(self, field):
        field_info = super(BaseSimpleMetadata, self).get_field_info(field)
        if self.schema_class and self.schema_class.get_extra_schema():
            extra = self.schema_class.get_extra_schema().get(field.field_name, None)
            if extra and isinstance(extra, dict):
                field_info.update(extra)
        return field_info


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
        metadata['columns'] = self.get_model_info(view.model_class)
        return metadata

    def get_model_info(self, model):
        if not model:
            return list()
        return [
            self.get_field_info(field) for field in model._meta.fields
        ]

    def get_field_info(self, field):
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
        return field_info
