import { useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';

import cloudApi from '../api/cloudApi';
import { cloudQueryKeys } from '../constants/queryKeys';

export function useUnlinkConnection() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (uuid) => cloudApi.unlinkConnection(uuid),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: cloudQueryKeys.connections() });
      toast.success('Cloud connection removed.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not remove cloud connection.');
    },
  });
}
