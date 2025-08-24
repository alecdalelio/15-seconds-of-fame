import { useQuery } from '@tanstack/react-query';
import { healthCheck } from '../services/api';

export const useHealthCheck = () => {
  return useQuery({
    queryKey: ['health'],
    queryFn: healthCheck,
    refetchInterval: 30000, // Check every 30 seconds
    retry: 3,
  });
};
