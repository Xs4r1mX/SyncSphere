import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import authApi from '../api/authApi';
import { PATHS } from '@/app/routes/paths';

export function useResetPassword() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authApi.resetPassword,
    onSuccess: () => {
      toast.success('Password reset successfully. Please log in.');
      navigate(PATHS.LOGIN, { replace: true });
    },
  });
}
