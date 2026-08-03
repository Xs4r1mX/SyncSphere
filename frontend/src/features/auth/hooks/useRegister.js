import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

import authApi from '../api/authApi';
import { PATHS } from '@/app/routes/paths';

export function useRegister() {
  const navigate = useNavigate();

  return useMutation({
    mutationFn: authApi.register,
    onSuccess: (user) => {
      toast.success('Account created. Check your email to verify it.');
      navigate(PATHS.VERIFY_EMAIL, {
        replace: true,
        state: {
          email: user?.email,
        },
      });
    },
  });
}
