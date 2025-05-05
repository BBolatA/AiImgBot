from django.views.generic import TemplateView
from django.db.models import Count
from django.db.models.functions import TruncDate
from generation.models import GeneratedImage


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["uid"] = self.request.GET.get("uid")
        tg_id = self.request.GET.get("uid")
        qs = GeneratedImage.objects.filter(task__status="READY")
        if tg_id:
            qs = qs.filter(task__tg_chat_id=tg_id)

        ctx["total_images"] = qs.count()

        daily = (
            qs.annotate(d=TruncDate("task__created_at"))
              .values("d").annotate(c=Count("id"))
        )
        ctx["avg_per_day"] = (
            sum(r["c"] for r in daily)/len(daily) if daily else 0
        )
        ctx["last_images"] = qs.select_related("task").order_by("-id")[:3]
        ctx["TELEGRAM_BOT_USERNAME"] = ""
        return ctx

