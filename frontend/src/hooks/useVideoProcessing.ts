import { useMutation } from '@tanstack/react-query';
import { processVideo } from '../services/api';
import type { ProcessVideoRequest } from '../types/api';

export const useVideoProcessing = () => {
  return useMutation({
    mutationFn: (request: ProcessVideoRequest) => processVideo(request),
    onError: (error) => {
      console.error('Video processing error:', error);
    },
  });
};
