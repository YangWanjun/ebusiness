import datetime
import django_filters
from rest_framework.response import Response

from . import models, serializers, biz
from utils.rest_base import BaseReadOnlyModelViewSet, BaseApiView


class TurnoverMonthlyViewSet(BaseReadOnlyModelViewSet):
    queryset = models.TurnoverMonthly.objects.all()
    serializer_class = serializers.TurnoverMonthlySerializer
    list_display = (
        'ym', 'cost', 'turnover_amount', 'tax_amount', 'expenses_amount', 'amount',
        'profit_amount', 'profit_rate'
    )
    list_display_links = ('ym',)
    filter_fields = ('year', 'month')


class TurnoverMonthlyChartView(BaseApiView):
    """月単位の売上情報を最近の12か月間表示する
    """

    def get(self, request, *args, **kwargs):
        data = biz.get_turnover_monthly_chart()
        return Response({'data': data})


class TurnoverYearlyChartView(BaseApiView):
    """年間売上情報を表示する
    """

    def get(self, request, *args, **kwargs):
        data = biz.get_turnover_yearly_chart()
        return Response({'data': data})


class TurnoverMonthlyByDivisionChartView(BaseApiView):

    def get(self, request, *args, **kwargs):
        data = biz.get_turnover_monthly_by_department_chart()
        return Response({'data': data})


class TurnoverCustomersByMonthFilter(django_filters.FilterSet):

   class Meta:
        model = models.TurnoverCustomersByMonth
        fields = {
            'customer_name': ['icontains'],
        }


class TurnoverCustomersByMonthViewSet(BaseReadOnlyModelViewSet):
    queryset = models.TurnoverCustomersByMonth.objects.all()
    serializer_class = serializers.TurnoverCustomersByMonthSerializer
    list_display = (
        'customer_name', 'cost', 'turnover_amount', 'tax_amount', 'expenses_amount', 'amount',
        'profit_amount', 'profit_rate'
    )
    list_display_links = ('customer_name',)
    filter_fields = ('customer_name',)
    filter_class = TurnoverCustomersByMonthFilter

    def get_queryset(self):
        today = datetime.date.today()
        year = self.request.GET.get('year', today.strftime('%Y'))
        month = self.request.GET.get('month', today.strftime('%m'))
        return self.queryset.filter(year=year, month=month)


class TurnoverCustomerByMonthFilter(django_filters.FilterSet):

   class Meta:
        model = models.TurnoverProject
        fields = {
            'project_name': ['icontains'],
        }


class TurnoverProjectViewSet(BaseReadOnlyModelViewSet):
    queryset = models.TurnoverProject.objects.all()
    serializer_class = serializers.TurnoverProjectSerializer
    list_display = (
        'project_name', 'cost', 'turnover_amount', 'tax_amount', 'expenses_amount', 'amount',
        'profit_amount', 'profit_rate'
    )
    list_display_links = ('project_name',)
    filter_fields = ('project_name',)
    filter_class = TurnoverCustomerByMonthFilter

    def get_queryset(self):
        today = datetime.date.today()
        year = self.request.GET.get('year', today.strftime('%Y'))
        month = self.request.GET.get('month', today.strftime('%m'))
        customer_id = self.request.GET.get('customer_id', None)
        if self.kwargs:
            return self.queryset.filter(year=year, month=month)
        elif customer_id:
            return self.queryset.filter(year=year, month=month, customer_id=customer_id)
        else:
            return self.queryset.none()


class TurnoverMemberViewSet(BaseReadOnlyModelViewSet):
    queryset = models.TurnoverMember.objects.all()
    serializer_class = serializers.TurnoverMemberSerializer
    list_display = (
        'name', 'org_name', 'cost', 'turnover_amount', 'expenses_amount',
        'profit_amount', 'profit_rate'
    )

    def get_queryset(self):
        today = datetime.date.today()
        year = self.request.GET.get('year', today.strftime('%Y'))
        month = self.request.GET.get('month', today.strftime('%m'))
        project_id = self.request.GET.get('project_id', None)
        if project_id:
            return self.queryset.filter(year=year, month=month, project__pk=project_id)
        else:
            return self.queryset.none()
