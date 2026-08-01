import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import authApi from '../api/authApi';

export function useForgotPassword() {
  return useMutation({
    mutationFn: authApi.forgotPassword,
    onSuccess: () => {
      toast.success('If the account exists, a reset link has been sent.');
    },
  });
}
