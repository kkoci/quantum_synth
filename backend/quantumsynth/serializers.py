"""
Serializers for Quantum Synth API
"""
from rest_framework import serializers
from .models import QuantumPatch, ProcessedSample


class QuantumPatchSerializer(serializers.ModelSerializer):
    """
    Serializer for QuantumPatch model
    """
    class Meta:
        model = QuantumPatch
        fields = [
            'id',
            'name',
            'description',
            'scheme',
            'shots',
            'buffer_size',
            'parameters',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProcessedSampleSerializer(serializers.ModelSerializer):
    """
    Serializer for ProcessedSample model
    """
    patch_name = serializers.CharField(source='patch.name', read_only=True)
    
    class Meta:
        model = ProcessedSample
        fields = [
            'id',
            'patch',
            'patch_name',
            'input_hash',
            'sample_rate',
            'duration',
            'created_at'
        ]
        read_only_fields = ['created_at']


class AudioProcessRequestSerializer(serializers.Serializer):
    """
    Serializer for audio processing request
    """
    audio = serializers.FileField(required=True)
    scheme = serializers.ChoiceField(
        choices=['qpam', 'sqpam', 'msqpam', 'qsm', 'mqsm'],
        default='qpam'
    )
    shots = serializers.IntegerField(
        default=4000,
        min_value=1000,
        max_value=8000
    )
    buffer_size = serializers.IntegerField(default=256, min_value=128, max_value=1024)
    use_patch = serializers.IntegerField(required=False, allow_null=True)


class TaskStatusSerializer(serializers.Serializer):
    """
    Serializer for Celery task status
    """
    task_id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
