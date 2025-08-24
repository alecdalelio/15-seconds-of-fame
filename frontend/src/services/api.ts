import axios from 'axios';
import type { ProcessVideoRequest, ProcessVideoResponse, HealthCheckResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutes for video processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Health check
export const healthCheck = async (): Promise<HealthCheckResponse> => {
  const response = await api.get<HealthCheckResponse>('/');
  return response.data;
};

// Process video
export const processVideo = async (request: ProcessVideoRequest): Promise<ProcessVideoResponse> => {
  const response = await api.post<ProcessVideoResponse>('/process', request);
  return response.data;
};

// Error handler
export const handleApiError = (error: any): string => {
  if (axios.isAxiosError(error)) {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.code === 'ECONNABORTED') {
      return 'Request timed out. Video processing may take a while.';
    }
    if (error.code === 'NETWORK_ERROR') {
      return 'Network error. Please check your connection.';
    }
    return error.message || 'An error occurred while processing the video.';
  }
  return 'An unexpected error occurred.';
};
