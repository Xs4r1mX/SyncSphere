import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import cloudApi from '../api/cloudApi';

export function useConnectProvider() {
  return useMutation({
    mutationFn: (provider) => cloudApi.authorizeProvider(provider),
    onSuccess: (data) => {
      if (data?.authorization_url) {
        window.location.assign(data.authorization_url);
        return;
      }

      toast.error('Could not start cloud authorization.');
    },
    onError: (error) => {
      toast.error(error.message || 'Could not start cloud authorization.');
    },
  });
}
