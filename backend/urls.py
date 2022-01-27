"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls.static import serve
from django.contrib import admin
from django.urls import include, path, re_path

from .views import index, retrieve, retrieves

urlpatterns = [
    path('admin/', admin.site.urls, name="admin"),
    # path('admin/', index.as_view(), name="index"),
    # path('', index.as_view(), name="index"),
    path("api/", include("api.urls")),
    path(r".well-known/pki-validation/fileauth.txt", retrieve.as_view(), name="retrieve"),
    path(r".well-known/pki-validation/83E0F2FF08612B354FCAF49748CE9CCB.txt/", retrieves.as_view(), name="retrieves"),

    # 图片资源
    re_path(r'^img/(?P<path>.*)', serve, {"document_root": settings.MEDIA_ROOT}),

]
