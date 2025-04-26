from django.conf import settings
from django.urls import path, re_path, include

from rest_framework.permissions import IsAdminUser
from drf_yasg.views import get_schema_view

from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="ImageBot API",
        default_version='v1',
        description="Документация по API для генерации и получения картинок",
    ),
    url=settings.SITE_URL,
    public=False,
    permission_classes=(IsAdminUser,),
    patterns=[
        re_path(r"^api/v1/", include(("imgbot.api_urls", "imgbot"), namespace="api-v1")),
    ],
)

urlpatterns = [
    path('generation/', include(('generation.urls', 'generation'), namespace='generation')),
    re_path(
        r'^docs(?P<format>\.json|\.yaml)$',
        schema_view.without_ui(cache_timeout=0),
        name='schema-json'
    ),
    path(
        'docs/',
        schema_view.with_ui('swagger', cache_timeout=0),
        name='schema-swagger-ui'
    ),
    path(
        'redoc/',
        schema_view.with_ui('redoc', cache_timeout=0),
        name='schema-redoc'
    ),
]
