from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_extensions.mixins import NestedViewSetMixin

from . import models, serializers, biz
from utils.rest_base import BaseModelViewSet, BaseApiView


class MeApiView(BaseApiView):

    def post(self, request, *args, **kwargs):
        data = biz.get_me(request.user)
        return Response(data)


class DashboardApiView(BaseApiView):

    def get_context_data(self, **kwargs):
        return {
            'brief_status': biz.get_brief_status(),
            'member_working_status': biz.get_member_working_status(),
            'partner_working_status': biz.get_partner_working_status(),
        }


class MemberViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.Member.objects.all()
    serializer_class = serializers.MemberSerializer

    @action(methods=['get'], url_path='quick-list', detail=False)
    def quick_list(self, *args, **kwargs):
        data = biz.get_member_list()
        return Response({
            'count': len(data),
            'results': data
        })

    @action(methods=['get'], url_path='history', detail=True)
    def history(self, *args, **kwargs):
        pk = kwargs.get('pk')
        member = self.get_object()
        return Response({
            'member': serializers.MemberSerializer(member).data,
            'projects': biz.get_project_history(pk),
            'organizations': biz.get_organization_history(pk),
            'salesperson': biz.get_salesperson_history(pk),
        })

    @action(methods=['get'], url_path='project-history', detail=True)
    def project_history(self, *args, **kwargs):
        data = biz.get_project_history(kwargs.get('pk'))
        return Response(data)

    @action(methods=['get'], url_path='organization-history', detail=True)
    def organization_history(self, *args, **kwargs):
        data = biz.get_organization_history(kwargs.get('pk'))
        return Response(data)

    @action(methods=['get'], url_path='salesperson-history', detail=True)
    def salesperson_history(self, *args, **kwargs):
        data = biz.get_salesperson_history(kwargs.get('pk'))
        return Response(data)


class SalespersonViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.Salesperson.objects.all()
    serializer_class = serializers.SalespersonSerializer


class SalespersonPeriodViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.SalespersonPeriod.objects.all()
    serializer_class = serializers.SalespersonPeriodSerializer


class OrganizationPeriodViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.OrganizationPeriod.objects.all()
    serializer_class = serializers.OrganizationPeriodSerializer


class OrganizationViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.Organization.objects.all().order_by('-is_on_sales', 'org_type', 'name')
    serializer_class = serializers.OrganizationSerializer
    pagination_class = None

    @action(methods=['get'], url_path='quick-list', detail=False)
    def quick_list(self, *args, **kwargs):
        data = biz.get_organization_list()
        return Response({
            'count': len(data),
            'results': data
        })

    @action(methods=['get'], detail=True)
    def members(self, *args, **kwargs):
        data = biz.get_organization_members(kwargs.get('pk'))
        return Response({
            'count': len(data),
            'results': data
        })


class PositionShipViewSet(NestedViewSetMixin, BaseModelViewSet):
    queryset = models.PositionShip.objects.all()
    serializer_class = serializers.PositionShipSerializer


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
