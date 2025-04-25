from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import TaskCreateSerializer, TaskStatusSerializer, UserImageSerializer
from .models import GenerationTask, GeneratedImage
from .tasks import run_generation


class GenerateAPIView(APIView):
    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except Exception:
            raise
        task = serializer.save(status='PENDING')
        run_generation.delay(task.id)
        return Response({"task_id": task.id}, status=status.HTTP_201_CREATED)


class StatusAPIView(APIView):
    def get(self, request, pk):
        task = GenerationTask.objects.get(pk=pk)
        resp = TaskStatusSerializer(task).data
        return Response(resp)


class UserImagesAPIView(APIView):
    def get(self, request):
        tg_id = request.GET.get("user_id")
        if not tg_id:
            return Response([])

        images = GeneratedImage.objects.filter(
            task__tg_chat_id=tg_id,
            task__status='READY'
        ).order_by('-task__created_at')

        serializer = UserImageSerializer(images, many=True, context={'request': request})
        return Response(serializer.data)