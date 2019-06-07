from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^pdf_preview$', views.PreviewPdfView.as_view(),),
]
