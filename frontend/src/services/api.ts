import axios from 'axios';

const API_BASE_URL = '/api/quantum';

interface ProcessAudioResponse {
  task_id: string;
  status: string;
  message: string;
}

interface TaskStatusResponse {
  task_id: string;
  status: string;
  result?: {
    status: string;
    audio: number[];
    metadata: {
      scheme: string;
      shots: number;
      sample_rate: number;
      samples: number;
      duration: number;
    };
  };
  error?: string;
}

interface QuantumPatch {
  id: number;
  name: string;
  description: string;
  scheme: string;
  shots: number;
  buffer_size: number;
  parameters: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export const processAudio = async (
  audioBlob: Blob,
  scheme: string,
  shots: number,
  bufferSize: number = 256
): Promise<ProcessAudioResponse> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.wav');
  formData.append('scheme', scheme);
  formData.append('shots', shots.toString());
  formData.append('buffer_size', bufferSize.toString());

  const response = await axios.post<ProcessAudioResponse>(
    `${API_BASE_URL}/process/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};

export const checkTaskStatus = async (taskId: string): Promise<TaskStatusResponse> => {
  const response = await axios.get<TaskStatusResponse>(
    `${API_BASE_URL}/task/${taskId}/`
  );
  return response.data;
};

export const getPatches = async (): Promise<QuantumPatch[]> => {
  const response = await axios.get<QuantumPatch[]>(`${API_BASE_URL}/patches/`);
  return response.data;
};

export const createPatch = async (
  patchData: Partial<QuantumPatch>
): Promise<QuantumPatch> => {
  const response = await axios.post<QuantumPatch>(
    `${API_BASE_URL}/patches/`,
    patchData
  );
  return response.data;
};

export const quickProcess = async (
  audioBlob: Blob,
  scheme: string,
  shots: number
): Promise<{ audio: number[]; sample_rate: number; samples: number }> => {
  const formData = new FormData();
  formData.append('audio', audioBlob, 'audio.wav');
  formData.append('scheme', scheme);
  formData.append('shots', shots.toString());

  const response = await axios.post(
    `${API_BASE_URL}/quick-process/`,
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );

  return response.data;
};
