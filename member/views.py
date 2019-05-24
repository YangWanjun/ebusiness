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

    def get_list_display(self):
        return 'name', 'member_type', 'join_date', 'salesperson_name', 'division_name', 'partner_name'

    def get_context_data(self, **kwargs):
        search = self.request.GET.get('search', None)
        members = biz.search_member_by_name(search)
        return {
            'count': len(members),
            'results': members
        }


class OrganizationViewSet(BaseModelViewSet):
    queryset = models.Organization.objects.all()
    serializer_class = serializers.OrganizationSerializer
    pagination_class = None
    filter_fields = ('is_on_sales',)


class MemberListApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        members = biz.get_member_list()
        return {
            'count': len(members),
            'results': members
        }


class MemberDetailsApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        data = biz.get_member_details(kwargs.get('member_id'))
        return data


class OrganizationPeriodViewSet(BaseModelViewSet):
    queryset = models.OrganizationPeriod.objects.all()
    serializer_class = serializers.OrganizationPeriodSerializer
    filter_fields = ('member',)

    def get_queryset(self):
        queryset = super(OrganizationPeriodViewSet, self).get_queryset()
        member_id = self.request.GET.get('member')
        if member_id:
            return queryset.filter(member=member_id)
        else:
            return queryset


class DivisionListApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        qs_org = models.Organization.objects.filter(
            org_type='01',
            is_on_sales=True,
        )
        return {
            'count': qs_org.count(),
            'results': serializers.OrganizationSerializer(qs_org, many=True).data,
        }
