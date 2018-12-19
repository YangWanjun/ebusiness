import django_filters

from . import models, serializers
from utils.rest_base import BaseModelViewSet


class MemberFilter(django_filters.FilterSet):

   class Meta:
        model = models.Member
        fields = {
            'last_name': ['icontains'],
            'first_name': ['icontains'],
        }


class MemberViewSet(BaseModelViewSet):
    queryset = models.Member.objects.all()
    serializer_class = serializers.MemberSerializer
    list_display = ('full_name', 'gender', 'address')
    filter_fields = ('last_name', 'first_name')
    filter_class = MemberFilter
