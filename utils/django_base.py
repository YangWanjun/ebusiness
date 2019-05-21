from django.contrib.auth.decorators import login_required
from django.views.generic import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.utils.decorators import method_decorator


class BaseViewWithoutLogin(View, ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseViewWithoutLogin, self).get_context_data(**kwargs)
        return context

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        pass


class BaseTemplateViewWithoutLogin(TemplateResponseMixin, BaseViewWithoutLogin):

    def get_template_names(self):
        template_names = super(BaseTemplateViewWithoutLogin, self).get_template_names()
        return template_names


@method_decorator(login_required, name='dispatch')
class BaseView(BaseViewWithoutLogin):
    pass


@method_decorator(login_required, name='dispatch')
class BaseTemplateView(BaseTemplateViewWithoutLogin):
    pass
