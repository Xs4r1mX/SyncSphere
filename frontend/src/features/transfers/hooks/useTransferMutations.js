import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import transferApi from '../api/transferApi';
import { transferQueryKeys } from '../constants/queryKeys';

export function useCreateTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (payload) => transferApi.createTransfer(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: transferQueryKeys.all });
      toast.success('Transfer started.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not start transfer.');
    },
  });
}

export function useCancelTransfer() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (jobUuid) => transferApi.cancelTransfer(jobUuid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: transferQueryKeys.all });
      toast.success('Cancellation requested.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not cancel transfer.');
    },
  });
}
