from django.urls import path, include

from . import views
from .views import start

urlpatterns = [
    path('', views.start, name='start'),
    path('main/', views.index, name='index'),
    path('impressum/', views.imprint, name='imprint')
]