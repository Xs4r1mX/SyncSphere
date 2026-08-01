import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import authApi from '../api/authApi';
import { PATHS } from '@/app/routes/paths';

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authApi.register,
    onSuccess: () => {
      toast.success('Account created. Please verify your email before logging in.');
      navigate(PATHS.LOGIN, { replace: true });
    },
  });
}
