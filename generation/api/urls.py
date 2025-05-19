from django.urls import path

from .views import (
    GenerateAPIView,
    StatusAPIView,
    UserImagesAPIView, UserFullStatsAPIView, DailyPromptAPIView, QueueAPIView,
)

app_name = "generation-api"

urlpatterns = [
    path("generate/", GenerateAPIView.as_view(), name="generate"),
    path("status/<int:pk>/", StatusAPIView.as_view(), name="status"),
    path("images/", UserImagesAPIView.as_view(), name="user_images"),
    path("full_stats/", UserFullStatsAPIView.as_view(), name="user_full_stats"),
    path("prompts/of_day/", DailyPromptAPIView.as_view()),
    path("queue/", QueueAPIView.as_view()),
]
