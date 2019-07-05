from django.conf.urls import url

from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views


router = ExtendedSimpleRouter()
member_router = router.register(r'members', views.VMemberViewSet, basename='member')


urlpatterns = [
    # url(r'^$', views.VMemberViewSet.as_view(),),
]

urlpatterns += router.urls
