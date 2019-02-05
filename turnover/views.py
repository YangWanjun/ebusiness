from rest_framework.response import Response

from . import models, serializers, biz
from utils.rest_base import BaseModelViewSet, BaseApiView


class TurnoverMonthlyViewSet(BaseModelViewSet):
    queryset = models.TurnoverMonthly.objects.all()
    serializer_class = serializers.TurnoverMonthlySerializer
    list_display = ('ym', 'turnover_amount', 'tax_amount', 'expenses_amount', 'amount')
    filter_fields = ('year', 'month')


class TurnoverMonthlyChartView(BaseApiView):
    """月単位の売上情報を最近の12か月間表示する
    """

    def get(self, request):
        data = biz.get_turnover_monthly_chart()
        return Response({'data': data})


class TurnoverYearlyChartView(BaseApiView):
    """年間売上情報を表示する
    """

    def get(self, request):
        data = biz.get_turnover_yearly_chart()
        return Response({'data': data})


class TurnoverMonthlyByDivisionChartView(BaseApiView):

    def get(self, request):
        data = biz.get_turnover_monthly_by_department_chart()
        return Response({'data': data})
