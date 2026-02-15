"""
Celery tasks for quantum audio processing
"""
from celery import shared_task
import quantumaudio
import numpy as np
import io
import soundfile as sf
from typing import Dict, Any


@shared_task(bind=True, name='quantumsynth.process_quantum_audio')
def process_quantum_audio(
    self,
    audio_data: list,
    scheme: str = 'qpam',
    shots: int = 4000,
    buffer_size: int = 256,
    sample_rate: int = 22050
) -> Dict[str, Any]:
    """
    Process audio through quantum circuit
    
    Args:
        audio_data: List of audio samples (normalized -1.0 to 1.0)
        scheme: Quantum encoding scheme to use
        shots: Number of quantum measurements
        buffer_size: Size of processing chunks
        sample_rate: Audio sample rate
        
    Returns:
        Dictionary containing processed audio and metadata
    """
    try:
        # Convert list back to numpy array
        data = np.array(audio_data, dtype=np.float32)

        print(f"[CELERY DEBUG] Received data length: {len(data)}")
        print(f"[CELERY DEBUG] Scheme: {scheme}, Shots: {shots}, Buffer: {buffer_size}")

        # Initialize the scheme
        try:
            qa_scheme = quantumaudio.load_scheme(scheme)
            if qa_scheme is None:
                raise ValueError(f"Scheme '{scheme}' returned None - may not be implemented")
        except Exception as scheme_error:
            print(f"[CELERY ERROR] Failed to load scheme '{scheme}': {scheme_error}")
            raise ValueError(f"Scheme '{scheme}' is not available or not implemented: {scheme_error}")
        
        # Process audio - quantumaudio.stream() doesn't take buffer_size
        # Instead, it processes the entire audio through quantum circuits
        print(f"[CELERY DEBUG] Using stream processing")
        processed = quantumaudio.stream(
            data,
            scheme=qa_scheme,
            shots=shots
        )
        
        # Ensure output is normalized
        processed = np.clip(processed, -1.0, 1.0)
        
        print(f"[CELERY DEBUG] Processed length: {len(processed)}")
        
        return {
            'status': 'success',
            'audio': processed.tolist(),
            'metadata': {
                'scheme': scheme,
                'shots': shots,
                'buffer_size': buffer_size,
                'sample_rate': sample_rate,
                'samples': len(processed),
                'duration': len(processed) / sample_rate
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task(bind=True, name='quantumsynth.process_audio_file')
def process_audio_file(
    self,
    audio_file_path: str,
    scheme: str = 'qpam',
    shots: int = 4000,
    buffer_size: int = 256
) -> Dict[str, Any]:
    """
    Process audio file through quantum circuit
    
    Args:
        audio_file_path: Path to audio file
        scheme: Quantum encoding scheme
        shots: Number of quantum measurements
        buffer_size: Size of processing chunks
        
    Returns:
        Dictionary with processed audio data
    """
    try:
        # Load audio file
        data, sample_rate = sf.read(audio_file_path)
        
        # Convert to mono if stereo (or use multi-channel schemes)
        if len(data.shape) > 1:
            if scheme in ['mqsm', 'msqpam']:
                # Keep stereo for multi-channel schemes
                data = data.T  # Transpose to (channels, samples)
            else:
                # Convert to mono
                data = np.mean(data, axis=1)
        
        # Normalize to -1.0 to 1.0 range
        if data.dtype == np.int16:
            data = data.astype(np.float32) / 32768.0
        elif data.dtype == np.int32:
            data = data.astype(np.float32) / 2147483648.0
        
        # Process through quantum circuit
        qa_scheme = quantumaudio.load_scheme(scheme)
        
        if len(data) > buffer_size:
            processed = quantumaudio.stream(
                data,
                scheme=qa_scheme,
                buffer_size=buffer_size,
                shots=shots
            )
        else:
            circuit = qa_scheme.encode(data)
            processed = qa_scheme.decode(circuit, shots=shots)
        
        return {
            'status': 'success',
            'audio': processed.tolist(),
            'metadata': {
                'scheme': scheme,
                'shots': shots,
                'sample_rate': int(sample_rate),
                'samples': len(processed),
                'duration': len(processed) / sample_rate
            }
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }
