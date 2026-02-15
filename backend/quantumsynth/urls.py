"""
URL configuration for quantumsynth app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'patches', views.QuantumPatchViewSet, basename='patch')

urlpatterns = [
    path('', include(router.urls)),
    path('process/', views.process_audio, name='process-audio'),
    path('quick-process/', views.quick_process, name='quick-process'),
    path('task/<str:task_id>/', views.task_status, name='task-status'),
]
