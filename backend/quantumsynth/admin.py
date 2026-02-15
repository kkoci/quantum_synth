"""
Admin configuration for Quantum Synth
"""
from django.contrib import admin
from .models import QuantumPatch, ProcessedSample


@admin.register(QuantumPatch)
class QuantumPatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'scheme', 'shots', 'buffer_size', 'created_at']
    list_filter = ['scheme', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ProcessedSample)
class ProcessedSampleAdmin(admin.ModelAdmin):
    list_display = ['patch', 'duration', 'sample_rate', 'created_at']
    list_filter = ['patch', 'created_at']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        return False  # Samples are created programmatically
