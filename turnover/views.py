from . import models, serializers
from utils.rest_base import BaseModelViewSet


class TurnoverMonthlyViewSet(BaseModelViewSet):
    queryset = models.TurnoverMonthly.objects.all()
    serializer_class = serializers.TurnoverMonthlySerializer
    list_display = ('ym', 'turnover_amount', 'tax_amount', 'expenses_amount', 'amount')
    filter_fields = ('year', 'month')
