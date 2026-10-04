"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from django.urls import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect


@csrf_protect
def index_view(request):
    """Serve the SPA template and make sure a CSRF cookie is set.

    The chat composer's fetch calls (chat / remember / recall / forget) are
    same-origin JSON requests that send the X-CSRFToken header read from the
    csrftoken cookie, which CsrfViewMiddleware requires for POST/DELETE.
    """
    response = TemplateResponse(request, 'index.html')
    response.render()
    return response


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('memory.urls')),
    path('', index_view, name='index'),
]
