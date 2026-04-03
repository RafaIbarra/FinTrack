"""
URL configuration for FinTrackProject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path,include
#from FinTrackApp.Urls.admin_urls
#from FinTrackApp.Urls.referenciales_urls
#from FinTrackApp.Urls.operaciones_urls
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/admin/', include('FinTrackApp.Urls.admin_urls')),
    path('api/sessions/', include('FinTrackApp.Urls.sesions_urls')),
    path('api/ref/', include('FinTrackApp.Urls.referenciales_urls')),
    path('api/operaciones/', include('FinTrackApp.Urls.operaciones_urls')),
]
