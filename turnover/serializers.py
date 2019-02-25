from rest_framework import serializers

from . import models
from utils.rest_base import BaseModelSerializer


class TurnoverMonthlySerializer(BaseModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.TurnoverMonthly
        fields = '__all__'

    def get_url(self, obj):
        return '/turnover/monthly/{pk}/'.format(pk=obj.pk)


class TurnoverYearlySerializer(BaseModelSerializer):

    class Meta:
        model = models.TurnoverYearly
        fields = '__all__'


class TurnoverClientsByMonthSerializer(BaseModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.TurnoverClientsByMonth
        fields = '__all__'

    def get_url(self, obj):
        return '/turnover/month/{year}{month}/client/{pk}/'.format(pk=obj.pk, year=obj.year, month=obj.month)


class TurnoverClientByMonthSerializer(BaseModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = models.TurnoverClientByMonth
        fields = '__all__'

    def get_url(self, obj):
        return '/turnover/month/{year}{month}/project/{pk}/'.format(pk=obj.pk, year=obj.year, month=obj.month)


class TurnoverMemberSerializer(BaseModelSerializer):

    class Meta:
        model = models.TurnoverMember
        fields = '__all__'
