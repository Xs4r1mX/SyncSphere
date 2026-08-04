import { useMutation } from '@tanstack/react-query';
import { toast } from 'sonner';

import authApi from '../api/authApi';

export function useForgotPassword() {
  return useMutation({
    mutationFn: authApi.forgotPassword,
    onSuccess: (data) => {
      if (data?.message) {
        toast.success(data.message);
      }
    },
  });
}
