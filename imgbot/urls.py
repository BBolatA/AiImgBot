"""
URL configuration for imgbot project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from core.auth.login_view import TelegramWebAppLoginAPIView
from generation.views import HomeView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin/", admin.site.urls),
    path("gallery/", TemplateView.as_view(template_name="gallery.html"), name="gallery"),
    path("analytics/", TemplateView.as_view(template_name="analytics.html"), name="analytics"),
    path("generation/", include("generation.urls")),
    path("api/v1/", include(("imgbot.api_urls", "imgbot"), namespace="api-v1")),
    path("api/v1/auth/login/", TelegramWebAppLoginAPIView.as_view()),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
