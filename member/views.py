import django_filters

from rest_framework.response import Response

from . import models, serializers, biz
from utils.rest_base import BaseModelViewSet, BaseApiView


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
    list_display = ('full_name', 'gender', 'address', 'join_date')
    filter_fields = ('last_name', 'first_name')
    filter_class = MemberFilter


class MeApiView(BaseApiView):

    def post(self, request, *args, **kwargs):
        data = biz.get_me(request.user)
        return Response(data)


class SearchMemberView(BaseApiView):
    model_class = models.SearchMember

    def get(self, request, *args, **kwargs):
        search = request.GET.get('search', None)
        members = biz.search_member_by_name(search)
        return Response({
            'count': len(members),
            'results': members
        })
