from collections import OrderedDict

from rest_framework.metadata import SimpleMetadata


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
