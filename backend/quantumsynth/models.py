"""
Models for Quantum Synth application
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class QuantumPatch(models.Model):
    """
    Stores quantum processing configuration presets
    """
    SCHEME_CHOICES = [
        ('qpam', 'QPAM - Quantum Probability Amplitude Modulation'),
        ('sqpam', 'SQPAM - Single-Qubit PAM'),
        ('msqpam', 'MSQPAM - Multi-channel Single-Qubit PAM'),
        ('qsm', 'QSM - Quantum State Modulation'),
        ('mqsm', 'MQSM - Multi-channel Quantum State Modulation'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    scheme = models.CharField(max_length=10, choices=SCHEME_CHOICES, default='qpam')
    shots = models.IntegerField(
        default=4000,
        validators=[MinValueValidator(1000), MaxValueValidator(8000)]
    )
    buffer_size = models.IntegerField(default=256)
    parameters = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.get_scheme_display()})"


class ProcessedSample(models.Model):
    """
    Stores processed audio samples for caching
    """
    patch = models.ForeignKey(
        QuantumPatch, 
        on_delete=models.CASCADE,
        related_name='processed_samples'
    )
    input_hash = models.CharField(max_length=64, db_index=True)
    output_audio = models.BinaryField()
    sample_rate = models.IntegerField(default=22050)
    duration = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patch', 'input_hash']),
        ]
    
    def __str__(self):
        return f"Sample for {self.patch.name} ({self.duration:.2f}s)"
