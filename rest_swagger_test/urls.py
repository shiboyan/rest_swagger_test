"""rest_swagger_test URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
import openapi as openapi
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include
from rest_framework.permissions import IsAdminUser
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from musics import views

# router = DefaultRouter()
# router.register(r'music', views.MusicViewSet)
#
# urlpatterns = [
#     url(r'^admin/', admin.site.urls),
#     url(r'^api/', include(router.urls)),
#     url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
# ]
SchemaView = get_schema_view(
    openapi.Info(
        title="Student and Instance Service API",
        default_version='v1'
    ),
    # validators=['flex', 'ssv'],
    public=False,
    permission_classes=(IsAdminUser,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/rest-auth/', include('rest_auth.urls')),
    path('', include('authentication.api.urls')),
    path('swagger/', SchemaView.with_ui(
        'swagger', cache_timeout=0), name='schema-swagger-ui')
]
