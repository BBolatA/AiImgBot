from django.urls import path
from generation import views as g
from django.views.generic import TemplateView

from generation.views import UserImagesAPIView

app_name = 'generation'
urlpatterns = [
    path('generate/', g.GenerateAPIView.as_view()),
    path('status/<int:pk>/', g.StatusAPIView.as_view()),
    path("images/", UserImagesAPIView.as_view(), name="user_images"),
]

