"""ebusiness URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin

from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

from master import views as master_api
from member import views as member_api
from partner import views as partner_api
from project import views as project_api
from turnover import views as turnover_api

router = routers.DefaultRouter()
router.register(r'project-stage', master_api.ProjectStageViewSet)
router.register(r'bank-account', master_api.BankAccountViewSet)
router.register(r'member', member_api.MemberViewSet)
router.register(r'salesperson', member_api.SalespersonViewSet)
router.register(r'organization', member_api.OrganizationViewSet)
router.register(r'organization-period', member_api.OrganizationPeriodViewSet)
router.register(r'salesperson-period', member_api.SalespersonPeriodViewSet)
router.register(r'position-ship', member_api.PositionShipViewSet)
router.register(r'partner', partner_api.PartnerViewSet)
router.register(r'customer', project_api.CustomerViewSet)
router.register(r'customer-member', project_api.CustomerMemberViewSet)
router.register(r'project', project_api.ProjectViewSet)
router.register(r'vproject', project_api.VProjectViewSet)
router.register(r'project_member', project_api.ProjectMemberViewSet)
router.register(r'member-attendance', project_api.MemberAttendanceViewSet)
router.register(r'customer-order', project_api.CustomerOrderViewSet)
router.register(r'turnover/monthly', turnover_api.TurnoverMonthlyViewSet)
router.register(r'turnover/customers_by_month', turnover_api.TurnoverCustomersByMonthViewSet)
router.register(r'turnover/project', turnover_api.TurnoverProjectViewSet)
router.register(r'turnover/member', turnover_api.TurnoverMemberViewSet)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls')),
    url(r'^api/token-auth/', obtain_jwt_token),
    url(r'^api/', include(router.urls)),

    url(r'^api/me/$', member_api.MeApiView.as_view()),
    url(r'^api/members/$', member_api.MemberListApiView.as_view()),
    url(r'^api/member/(?P<member_id>\d+)/details/$', member_api.MemberDetailsApiView.as_view()),
    url(r'^api/member/search$', member_api.SearchMemberView.as_view()),
    url(r'^api/organization-division/$', member_api.DivisionListApiView.as_view()),
    url(r'^api/organization-view/$', member_api.OrganizationListApiView.as_view()),
    url(r'^api/organization-member/(?P<org_id>\d+)/$', member_api.OrganizationMemberApiView.as_view()),
    url(r'^api/project/search$', project_api.SearchProjectView.as_view()),
    url(r'^api/project/(?P<pk>\d+)/attendance$', project_api.ProjectAttendanceList.as_view()),
    url(r'^api/project/(?P<pk>\d+)/attendance/(?P<year>\d{4})/(?P<month>\d{2})$',
        project_api.ProjectAttendanceView.as_view()),
    url(r'^api/project/(?P<pk>\d+)/order$', project_api.ProjectOrderListView.as_view()),
    url(r'^api/project/request/(?P<request_no>\d{7})/$', project_api.ProjectRequestDetailApiView.as_view()),
    url(r'^api/project/(?P<project_id>\d+)/order/(?P<order_id>\d+)/request/create/(?P<year>\d{4})/(?P<month>\d{2})$',
        project_api.ProjectRequestCreateApiView.as_view()),
    url(r'^api/turnover/monthly/chart$', turnover_api.TurnoverMonthlyChartView.as_view()),
    url(r'^api/turnover/yearly/chart$', turnover_api.TurnoverYearlyChartView.as_view()),
    url(r'^api/turnover/division/monthly/chart$', turnover_api.TurnoverMonthlyByDivisionChartView.as_view()),
    url(r'^api/attachment/download/(?P<uuid>[0-9a-zA-z-_]+)$', master_api.FileDownloadApiView.as_view()),

    # url(r'^master/', include('master.urls')),
]
