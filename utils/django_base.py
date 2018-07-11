from django.db import models

from rest_framework.serializers import ModelSerializer


class BaseModel(models.Model):
    created_dt = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_dt = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        abstract = True


class BaseModelSerializer(models.Model):
    pass
