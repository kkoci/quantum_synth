"""
Views for Quantum Synth API
"""
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from celery.result import AsyncResult
from django.core.files.uploadedfile import InMemoryUploadedFile
import numpy as np
import soundfile as sf
import io
import hashlib
import quantumaudio
import librosa

from .models import QuantumPatch, ProcessedSample
from .serializers import (
    QuantumPatchSerializer,
    ProcessedSampleSerializer,
    AudioProcessRequestSerializer,
    TaskStatusSerializer
)
from .tasks import process_quantum_audio, process_audio_file


class QuantumPatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Quantum Patches
    """
    queryset = QuantumPatch.objects.all()
    serializer_class = QuantumPatchSerializer


@api_view(['POST'])
def process_audio(request):
    """
    Process audio through quantum circuit
    
    Accepts audio file upload and returns task ID
    """
    serializer = AudioProcessRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = serializer.validated_data['audio']
    scheme = serializer.validated_data.get('scheme', 'qpam')
    shots = serializer.validated_data.get('shots', 4000)
    buffer_size = serializer.validated_data.get('buffer_size', 256)
    
    # Optimize buffer size for complex schemes to reduce circuit depth
    if scheme in ['sqpam', 'qsm', 'mqsm']:
        buffer_size = min(buffer_size, 128)  # Smaller buffers = smaller circuits = faster
    
    try:
        # Read audio file using librosa (handles more formats than soundfile)
        audio_bytes = audio_file.read()
        
        print(f"[DEBUG] Received audio file: {len(audio_bytes)} bytes")
        print(f"[DEBUG] Scheme: {scheme}, Shots: {shots}")
        
        # Use librosa to load audio - it can handle WebM, MP3, etc.
        import librosa
        data, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=False)
        
        print(f"[DEBUG] Loaded audio shape: {data.shape}, sample_rate: {sample_rate}")
        
        # Librosa returns (samples,) for mono or (channels, samples) for stereo
        # Ensure we have the right shape
        if len(data.shape) == 1:
            # Mono audio
            pass  # Already correct shape
        elif len(data.shape) == 2:
            # Multi-channel - convert to mono if scheme doesn't support multi-channel
            if scheme not in ['mqsm', 'msqpam']:
                data = np.mean(data, axis=0)
        
        print(f"[DEBUG] Final data shape: {data.shape}, length: {len(data)}")
        
        # Librosa already returns float32 normalized to [-1, 1]
        
        # Start async task
        task = process_quantum_audio.delay(
            data.tolist(),
            scheme=scheme,
            shots=shots,
            buffer_size=buffer_size,
            sample_rate=int(sample_rate)
        )
        
        return Response({
            'task_id': task.id,
            'status': 'processing',
            'message': 'Audio processing started'
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def task_status(request, task_id):
    """
    Check status of a Celery task
    """
    task_result = AsyncResult(task_id)
    
    response_data = {
        'task_id': task_id,
        'status': task_result.status,
    }
    
    if task_result.ready():
        if task_result.successful():
            result = task_result.result
            if isinstance(result, dict) and result.get('status') == 'success':
                response_data['result'] = result
            else:
                response_data['status'] = 'FAILURE'
                response_data['error'] = result.get('error', 'Unknown error')
        else:
            response_data['status'] = 'FAILURE'
            response_data['error'] = str(task_result.result)
    
    return Response(response_data)


@api_view(['POST'])
def quick_process(request):
    """
    Quick audio processing for small samples (synchronous)
    Use only for very short audio clips
    """
    serializer = AudioProcessRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    audio_file = serializer.validated_data['audio']
    scheme = serializer.validated_data.get('scheme', 'qpam')
    shots = serializer.validated_data.get('shots', 4000)
    
    try:        
        # Read audio using librosa (handles WebM, MP3, etc.)
        audio_bytes = audio_file.read()
        data, sample_rate = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=False)
        
        # Handle mono/stereo
        if len(data.shape) == 2 and scheme not in ['mqsm', 'msqpam']:
            data = np.mean(data, axis=0)
        
        # Limit to short clips only
        if len(data) > 2048:
            return Response(
                {'error': 'Audio too long for quick processing. Use /process/ endpoint.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Process - load scheme first, then use stream
        print(f"[DEBUG] Loading scheme: {scheme}")
        try:
            qa_scheme = quantumaudio.load_scheme(scheme)
            if qa_scheme is None:
                raise ValueError(f"Scheme '{scheme}' is not implemented in quantumaudio")
        except Exception as scheme_error:
            print(f"[DEBUG] Failed to load scheme '{scheme}': {scheme_error}")
            raise ValueError(f"Scheme '{scheme}' is not available: {scheme_error}")

        print(f"[DEBUG] Scheme loaded, processing...")
        processed = quantumaudio.stream(data, scheme=qa_scheme, shots=shots)
        print(f"[DEBUG] Processing complete, output shape: {processed.shape}")

        # Handle both mono and multi-channel output
        num_samples = processed.shape[-1] if len(processed.shape) > 1 else len(processed)

        return Response({
            'audio': processed.tolist(),
            'sample_rate': int(sample_rate),
            'samples': num_samples
        })

    except Exception as e:
        print(f"[DEBUG] Quick process error: {e}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
