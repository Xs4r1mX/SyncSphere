import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import authApi from '../api/authApi';

export function useResendVerification() {
  return useMutation({
    mutationFn: authApi.resendVerification,
    onSuccess: () => {
      toast.success('Verification email sent again.');
    },
  });
}
