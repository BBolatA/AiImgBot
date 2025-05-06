from datetime import timedelta
from django.utils import timezone
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskCreateSerializer, TaskStatusSerializer, UserImageSerializer
from generation.models import GenerationTask, GeneratedImage
from generation.tasks import run_generation
from django.db.models import Count
from django.db.models.functions import TruncDate


class GenerateAPIView(APIView):
    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        task = serializer.save(
            tg_chat_id=request.tg_id,
            status="PENDING"
        )
        run_generation.delay(task.id)
        return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)


class StatusAPIView(APIView):
    def get(self, request, pk):
        task = get_object_or_404(GenerationTask, pk=pk, tg_chat_id=request.tg_id)
        return Response(TaskStatusSerializer(task).data)


class UserImagesAPIView(APIView):
    filter_backends = [OrderingFilter]
    ordering_fields = ['task__created_at']

    def get(self, request):
        qs = (GeneratedImage.objects
              .filter(task__tg_chat_id=request.tg_id,
                      task__status="READY"))

        if m := request.GET.get('model'):
            qs = qs.filter(task__base_model_name=m)

        if perf := request.GET.get('performance'):
            qs = qs.filter(task__performance_selection=perf)

        if aspect := request.GET.get('aspect'):
            qs = qs.filter(task__aspect_ratios_selection=aspect)

        if style := request.GET.get('style'):
            qs = qs.filter(task__style_selections__contains=[style])

        qs = qs.order_by('-task__created_at')

        limit = int(request.GET.get('limit') or 0)
        if limit:
            qs = qs[:limit]

        ser = UserImageSerializer(qs, many=True, context={'request': request})
        return Response(ser.data)


class UserFullStatsAPIView(APIView):
    def get(self, request):
        period = int(request.GET.get("period", "0") or 0)
        qs = GeneratedImage.objects.filter(
            task__tg_chat_id=request.tg_id,
            task__status="READY"
        ).select_related("task")
        if period:
            qs = qs.filter(task__created_at__gte=timezone.now()-timedelta(days=period))

        by_date = (
            qs.annotate(d=TruncDate("task__created_at"))
              .values("d").annotate(c=Count("id")).order_by("d")
        )

        by_style = (
            qs.values("task__style_selections")
              .annotate(c=Count("id")).order_by("-c")[:10]
        )

        by_model = (
            qs.values("task__base_model_name")
              .annotate(c=Count("id")).order_by("-c")[:10]
        )

        def fmt(qs, k): return [{"label": r[k] or "—", "count": r["c"]} for r in qs]

        return Response({
            "by_date":  [{"date": str(r["d"]), "count": r["c"]} for r in by_date],
            "by_style": fmt(by_style, "task__style_selections"),
            "by_model": fmt(by_model, "task__base_model_name"),
        })
