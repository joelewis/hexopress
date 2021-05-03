"""hexopress URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from hexo import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', views.index, name='index'),
    url(r'^privacy/', views.privacy_policy, name='privacy_policy'),
    url(r'^googlelogin/$', views.google_login, name='google_login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^refreshblog/$', views.refresh_blog, name='refresh_blog'),
    url(r'^generateblog/$', views.generate_blog, name='generate_blog'),
    url(r'^oauth2callback/$', views.oauth2callback),
    url(r'^login/$', views.refresh_accesstoken),
    url(r'^settings/blog/$', views.blog_settings),
    url(r'^settings/account/$', views.account_settings),

    url(r'^@(?P<username>[-\w.]+)/(?P<path>.*)$', views.serve_blog),
    url(r'^app/.*/$', views.index, name='index'),
]
