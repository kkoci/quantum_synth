import React, { useState, useCallback, useRef } from 'react';
import * as Tone from 'tone';
import { processAudio, checkTaskStatus, quickProcess } from '../services/api';
import './QuantumSynth.css';

interface QuantumSynthProps {}

const NOTES = ['C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4', 'C5'];
const SCHEMES = [
  { value: 'qpam', label: 'QPAM', description: 'Fast (~10s)' },
  { value: 'sqpam', label: 'SQPAM', description: 'Slow (~30 mins)' },
  { value: 'qsm', label: 'QSM', description: 'Slow (~30 mins)' },
  { value: 'mqsm', label: 'MQSM', description: 'Very Slow (~45 mins)' },
];

const QuantumSynth: React.FC<QuantumSynthProps> = () => {
  const [isProcessing, setIsProcessing] = useState(false);
  const [scheme, setScheme] = useState('qpam');
  const [shots, setShots] = useState(4000);
  const [status, setStatus] = useState('');
  const [lastProcessed, setLastProcessed] = useState<{
    audio: number[] | number[][],
    sampleRate: number,
    scheme: string,
    shots: number
  } | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);

  const initAudio = async () => {
    if (!audioContextRef.current) {
      await Tone.start();
      audioContextRef.current = new AudioContext();
    }
  };

  const generateAndProcess = async (note: string, duration: number = 0.5) => {
    await initAudio();
    setIsProcessing(true);
    setStatus('Generating audio...');

    try {
      // Generate basic waveform using Tone.js
      const synth = new Tone.Synth({
        oscillator: { type: 'sine' }
      }).toDestination();
      
      // Don't specify mimeType - let browser choose (usually webm)
      const recorder = new Tone.Recorder();
      synth.connect(recorder);

      recorder.start();
      synth.triggerAttackRelease(note, duration);

      await new Promise(resolve => setTimeout(resolve, duration * 1000 + 100));
      const recording = await recorder.stop();
      
      synth.dispose();

      // Send to backend for quantum processing
      setStatus('Processing through quantum circuit...');
      
      // Try quick process first (for small clips)
      try {
        console.log('Attempting quick process...');
        const quickResult = await quickProcess(recording, scheme, shots);
        console.log('Quick process result:', quickResult);

        // Save processed audio
        setLastProcessed({
          audio: quickResult.audio,
          sampleRate: quickResult.sample_rate,
          scheme,
          shots
        });

        setStatus('Playing quantum audio...');
        await playQuantumAudio(quickResult.audio, quickResult.sample_rate);
        setStatus('Complete! 🎵');
      } catch (quickError) {
        console.log('Quick process failed, trying async:', quickError);
        // Fall back to async processing
        const response = await processAudio(recording, scheme, shots);
        console.log('Async process started:', response);
        const result = await pollForResult(response.task_id);
        console.log('Async process complete:', result);

        if (result.audio) {
          // Save processed audio
          setLastProcessed({
            audio: result.audio,
            sampleRate: result.metadata.sample_rate,
            scheme,
            shots
          });

          setStatus('Playing quantum audio...');
          await playQuantumAudio(result.audio, result.metadata.sample_rate);
          setStatus('Complete! 🎵');
        }
      }
    } catch (error) {
      console.error('Full error:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        setStatus(`Error: ${JSON.stringify(error.response.data)}`);
      } else {
        setStatus(`Error: ${error.message || error}`);
      }
    } finally {
      setIsProcessing(false);
      setTimeout(() => setStatus(''), 3000);
    }
  };

  const pollForResult = async (taskId: string): Promise<any> => {
    // Different timeouts for different schemes
    const timeouts: { [key: string]: number } = {
      'qpam': 60,      // 60 seconds
      'sqpam': 1800,    // 30 minutes
      'qsm': 1800,      // 30 minutes
      'mqsm': 3600,     // 1 hour
    };
    
    const maxAttempts = timeouts[scheme] || 60;
    
    for (let i = 0; i < maxAttempts; i++) {
      const statusData = await checkTaskStatus(taskId);
      
      if (statusData.status === 'SUCCESS' && statusData.result) {
        return statusData.result;
      }
      
      if (statusData.status === 'FAILURE') {
        throw new Error(statusData.error || 'Processing failed');
      }
      
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // More informative status messages
      const mins = Math.floor(i / 60);
      const secs = i % 60;
      const timeStr = mins > 0 ? `${mins}m ${secs}s` : `${secs}s`;
      setStatus(`Processing quantum circuit... ${timeStr}`);
    }
    
    throw new Error(`Processing timeout after ${Math.floor(maxAttempts / 60)} minutes`);
  };

  const downloadWav = (audioData: number[] | number[][], sampleRate: number, filename: string) => {
    const isMultiChannel = Array.isArray(audioData[0]);
    const numChannels = isMultiChannel ? (audioData as number[][]).length : 1;
    const numSamples = isMultiChannel ? (audioData as number[][])[0].length : (audioData as number[]).length;

    // WAV file parameters
    const bytesPerSample = 2; // 16-bit audio
    const blockAlign = numChannels * bytesPerSample;
    const byteRate = sampleRate * blockAlign;
    const dataSize = numSamples * blockAlign;
    const fileSize = 44 + dataSize; // 44 bytes for WAV header

    // Create WAV file buffer
    const buffer = new ArrayBuffer(fileSize);
    const view = new DataView(buffer);

    // Write WAV header
    const writeString = (offset: number, string: string) => {
      for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, fileSize - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true); // fmt chunk size
    view.setUint16(20, 1, true); // PCM format
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, byteRate, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, bytesPerSample * 8, true); // bits per sample
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);

    // Write audio data
    let offset = 44;
    if (isMultiChannel) {
      const channels = audioData as number[][];
      for (let i = 0; i < numSamples; i++) {
        for (let ch = 0; ch < numChannels; ch++) {
          const sample = Math.max(-1, Math.min(1, channels[ch][i]));
          view.setInt16(offset, sample * 0x7FFF, true);
          offset += 2;
        }
      }
    } else {
      const monoData = audioData as number[];
      for (let i = 0; i < numSamples; i++) {
        const sample = Math.max(-1, Math.min(1, monoData[i]));
        view.setInt16(offset, sample * 0x7FFF, true);
        offset += 2;
      }
    }

    // Create blob and download
    const blob = new Blob([buffer], { type: 'audio/wav' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  const playQuantumAudio = async (audioData: number[] | number[][], sampleRate: number) => {
    if (!audioContextRef.current) return;

    console.log('Playing quantum audio:', {
      isMultiChannel: Array.isArray(audioData[0]),
      dataLength: audioData.length,
      sampleRate,
      firstFewSamples: Array.isArray(audioData[0]) ? audioData[0].slice(0, 5) : audioData.slice(0, 10)
    });

    if (!audioData || audioData.length === 0) {
      console.error('No audio data to play');
      setStatus('Error: No audio data received');
      return;
    }

    const audioContext = audioContextRef.current;

    // Handle multi-channel (stereo) or mono audio
    const isMultiChannel = Array.isArray(audioData[0]);

    if (isMultiChannel) {
      // Multi-channel audio: audioData is [[ch0 samples], [ch1 samples], ...]
      const channels = audioData as number[][];
      const numChannels = channels.length;
      const numSamples = channels[0].length;

      console.log(`Creating ${numChannels}-channel buffer with ${numSamples} samples`);
      const buffer = audioContext.createBuffer(numChannels, numSamples, sampleRate);

      // Set data for each channel
      for (let ch = 0; ch < numChannels; ch++) {
        buffer.getChannelData(ch).set(channels[ch]);
      }

      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start();
    } else {
      // Mono audio: audioData is [samples]
      const monoData = audioData as number[];
      console.log(`Creating mono buffer with ${monoData.length} samples`);
      const buffer = audioContext.createBuffer(1, monoData.length, sampleRate);

      buffer.getChannelData(0).set(monoData);

      const source = audioContext.createBufferSource();
      source.buffer = buffer;
      source.connect(audioContext.destination);
      source.start();
    }
  };

  return (
    <div className="quantum-synth">
      <div className="controls">
        <div className="control-group">
          <label>Quantum Scheme:</label>
          <select 
            value={scheme} 
            onChange={(e) => setScheme(e.target.value)}
            disabled={isProcessing}
          >
            {SCHEMES.map(s => (
              <option key={s.value} value={s.value}>{s.label} - {s.description}</option>
            ))}
          </select>
        </div>

        <div className="control-group">
          <label>Quantum Shots: {shots}</label>
          <input
            type="range"
            min="1000"
            max="8000"
            step="500"
            value={shots}
            onChange={(e) => setShots(parseInt(e.target.value))}
            disabled={isProcessing}
          />
          <small>Higher = more accurate, slower processing</small>
        </div>
      </div>

      <div className="keyboard">
        <h3>Play Notes:</h3>
        <div className="keys">
          {NOTES.map(note => (
            <button
              key={note}
              className="key"
              onClick={() => generateAndProcess(note)}
              disabled={isProcessing}
            >
              {note}
            </button>
          ))}
        </div>
      </div>

      {status && (
        <div className={`status ${isProcessing ? 'processing' : 'complete'}`}>
          {status}
        </div>
      )}

      {lastProcessed && !isProcessing && (
        <div className="download-section">
          <button
            className="download-btn"
            onClick={() => {
              const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
              const filename = `quantum_${lastProcessed.scheme}_${lastProcessed.shots}shots_${timestamp}.wav`;
              downloadWav(lastProcessed.audio, lastProcessed.sampleRate, filename);
            }}
          >
            💾 Download Last Output
          </button>
          <small>
            {lastProcessed.scheme.toUpperCase()} · {lastProcessed.shots} shots ·
            {Array.isArray(lastProcessed.audio[0]) ? ' Stereo' : ' Mono'}
          </small>
        </div>
      )}

      <div className="info">
        <h4>How it works:</h4>
        <ol>
          <li>Click a note to generate a pure tone</li>
          <li>Audio is encoded into a quantum circuit</li>
          <li>Circuit is executed with quantum measurements</li>
          <li>Results are decoded back into audio</li>
        </ol>
        <p>
          <strong>Quantum Effects:</strong> Lower shot counts introduce more quantum noise, 
          creating lo-fi artifacts. Different schemes produce different sonic characteristics.
        </p>
      </div>
    </div>
  );
};

export default QuantumSynth;
