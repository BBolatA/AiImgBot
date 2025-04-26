from django.urls import path
from generation.api import views as g
from generation.api.views import UserImagesAPIView

app_name = 'generation'
urlpatterns = [
    path('generate/', g.GenerateAPIView.as_view(), name='generate'),
    path('status/<int:pk>/', g.StatusAPIView.as_view(), name='status'),
    path("images/", UserImagesAPIView.as_view(), name="user_images"),
]
