from django.conf import settings
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["TELEGRAM_BOT_USERNAME"] = settings.TELEGRAM_BOT_USERNAME
        return ctx
