"""
App configuration for quantumsynth
"""
from django.apps import AppConfig


class QuantumsynthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quantumsynth'
    verbose_name = 'Quantum Synth'
