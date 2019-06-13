from django.conf.urls import url

from rest_framework_extensions.routers import ExtendedSimpleRouter

from . import views


router = ExtendedSimpleRouter()
member_router = router.register(r'members', views.MemberViewSet)
member_router.register(
    r'salesperson',
    views.SalespersonPeriodViewSet,
    basename='salesperson-periods',
    parents_query_lookups=['member']
)
member_router.register(
    r'organizations',
    views.OrganizationPeriodViewSet,
    basename='organization-periods',
    parents_query_lookups=['member']
)
router.register(r'salesperson', views.SalespersonViewSet)
router.register(r'salesperson-period', views.SalespersonPeriodViewSet)
router.register(r'organization-period', views.OrganizationPeriodViewSet)
organization_router = router.register(r'organizations', views.OrganizationViewSet)
organization_router.register(
    r'positions',
    views.PositionShipViewSet,
    basename='positions',
    parents_query_lookups=['organization']
)
router.register(r'position-ship', views.PositionShipViewSet)


urlpatterns = [
    url(r'^$', views.DashboardApiView.as_view(),),
]

urlpatterns += router.urls
